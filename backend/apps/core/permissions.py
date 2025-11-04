from functools import wraps
from rest_framework import permissions
from django.core.cache import cache
from .exceptions import PermissionDeniedError
import logging

logger = logging.getLogger(__name__)


class HasOrganizationPermission(permissions.BasePermission):
    """
    Check if user has specific permission in current organization context.
    Permission format: 'resource.action' (e.g., 'invoices.create')
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if organization context is set
        if not hasattr(request, 'organization_member'):
            return False
        
        # Get required permission from view
        required_permission = getattr(view, 'required_permission', None)
        if not required_permission:
            return True  # No specific permission required
        
        # Check permission
        return check_permission(
            request.user,
            request.organization,
            required_permission
        )


def check_permission(user, organization, permission_code):
    """
    Check if user has a specific permission in an organization.
    Uses Redis cache to avoid repeated database queries.
    
    Args:
        user: User instance
        organization: Organization instance
        permission_code: Permission code (e.g., 'invoices.create')
    
    Returns:
        bool: True if user has permission, False otherwise
    """
    # Create cache key
    cache_key = f"perms:{user.id}:{organization.id}:{permission_code}"
    
    # Try to get from cache
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result == 'true'
    
    # Query database
    from apps.organizations.models import OrganizationMember
    
    try:
        member = OrganizationMember.objects.select_related('role').get(
            user=user,
            organization=organization,
            is_active=True
        )
        
        # Check if role has the permission
        has_perm = member.role.permissions.filter(
            code=permission_code,
            is_active=True
        ).exists()
        
        # Cache result for 5 minutes
        cache.set(cache_key, 'true' if has_perm else 'false', 300)
        
        return has_perm
        
    except OrganizationMember.DoesNotExist:
        cache.set(cache_key, 'false', 300)
        return False


def invalidate_permission_cache(user, organization):
    """
    Invalidate all cached permissions for a user in an organization.
    Call this when user's role changes or role permissions are modified.
    """
    # Note: This is a simple implementation. In production, you might want
    # to maintain a list of cached keys for each user-org pair for efficient invalidation
    cache_pattern = f"perms:{user.id}:{organization.id}:*"
    logger.info(f"Invalidating permission cache: {cache_pattern}")
    # Django cache doesn't support pattern deletion by default
    # You'd need to maintain a list of keys or use Redis directly


def require_permission(permission_code):
    """
    Decorator to check if user has specific permission before executing view.
    
    Usage:
        @require_permission('invoices.create')
        def create_invoice(request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, 'organization'):
                raise PermissionDeniedError("Organization context not set")
            
            if not check_permission(request.user, request.organization, permission_code):
                logger.warning(
                    f"Permission denied: user={request.user.email}, "
                    f"org={request.organization.name}, "
                    f"permission={permission_code}"
                )
                raise PermissionDeniedError(
                    f"You need '{permission_code}' permission to perform this action"
                )
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


class IsOrganizationOwner(permissions.BasePermission):
    """Check if user is owner of the organization"""
    
    def has_permission(self, request, view):
        if not hasattr(request, 'organization_member'):
            return False
        return request.organization_member.role.name == 'Owner'


class IsOrganizationAdmin(permissions.BasePermission):
    """Check if user is admin or owner of the organization"""
    
    def has_permission(self, request, view):
        if not hasattr(request, 'organization_member'):
            return False
        return request.organization_member.role.name in ['Owner', 'Admin']