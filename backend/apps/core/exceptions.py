from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class TenantIsolationError(APIException):
    """Raised when tenant isolation is violated"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Access denied to this resource'
    default_code = 'tenant_isolation_error'


class PermissionDeniedError(APIException):
    """Raised when user doesn't have required permission"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to perform this action'
    default_code = 'permission_denied'


class RateLimitExceededError(APIException):
    """Raised when rate limit is exceeded"""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Too many requests. Please try again later.'
    default_code = 'rate_limit_exceeded'


class InvalidTokenError(APIException):
    """Raised when JWT token is invalid"""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Invalid or expired token'
    default_code = 'invalid_token'


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        # Standardize error response format
        error_data = {
            'error': {
                'message': str(exc),
                'code': getattr(exc, 'default_code', 'error'),
                'status_code': response.status_code,
            }
        }
        
        # Add field-specific errors if available
        if isinstance(response.data, dict):
            if 'detail' not in response.data:
                error_data['error']['fields'] = response.data
        
        response.data = error_data
        
        # Log errors
        if response.status_code >= 500:
            logger.error(
                f"Server error: {exc}",
                exc_info=True,
                extra={'context': context}
            )
    
    return response