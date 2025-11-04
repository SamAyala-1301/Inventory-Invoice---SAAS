import logging
import time
from threading import local
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from rest_framework import status

logger = logging.getLogger(__name__)

# Thread-local storage for request context
_thread_locals = local()


def get_current_organization():
    """Get the current organization from thread-local storage"""
    return getattr(_thread_locals, 'organization', None)


def get_current_user():
    """Get the current user from thread-local storage"""
    return getattr(_thread_locals, 'user', None)


class TenantContextMiddleware(MiddlewareMixin):
    """
    Middleware to handle multi-tenant context.
    Extracts organization from X-Organization-Id header and validates access.
    """
    
    def process_request(self, request):
        # Clear any existing context
        _thread_locals.organization = None
        _thread_locals.user = None
        
        # Skip for non-authenticated requests and auth endpoints
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None
            
        if request.path.startswith('/api/auth/') or request.path.startswith('/admin/'):
            return None
        
        # Store user in thread local
        _thread_locals.user = request.user
        
        # Get organization ID from header
        org_id = request.headers.get('X-Organization-Id')
        
        if not org_id:
            # For organization list endpoint, no org_id is required
            if request.path == '/api/organizations/' and request.method == 'GET':
                return None
            if request.path == '/api/organizations/' and request.method == 'POST':
                return None
                
            return JsonResponse(
                {'error': 'X-Organization-Id header is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate user has access to this organization
        try:
            from apps.organizations.models import OrganizationMember
            membership = OrganizationMember.objects.select_related('organization').get(
                user=request.user,
                organization_id=org_id,
                is_active=True
            )
            
            if not membership.organization.is_active:
                return JsonResponse(
                    {'error': 'Organization is inactive'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Set organization in thread local and request
            request.organization = membership.organization
            request.organization_member = membership
            _thread_locals.organization = membership.organization
            
            logger.debug(
                f"Tenant context set: user={request.user.email}, "
                f"org={membership.organization.name}"
            )
            
        except OrganizationMember.DoesNotExist:
            return JsonResponse(
                {'error': 'You do not have access to this organization'},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            logger.error(f"Error in TenantContextMiddleware: {str(e)}")
            return JsonResponse(
                {'error': 'Invalid organization context'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return None


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all API requests with timing information.
    """
    
    def process_request(self, request):
        request.start_time = time.time()
        
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Log API requests (skip static files)
            if request.path.startswith('/api/'):
                user_email = getattr(request.user, 'email', 'anonymous')
                org_name = getattr(getattr(request, 'organization', None), 'name', 'N/A')
                
                logger.info(
                    f"{request.method} {request.path} | "
                    f"User: {user_email} | "
                    f"Org: {org_name} | "
                    f"Status: {response.status_code} | "
                    f"Duration: {duration:.3f}s"
                )
        
        return response