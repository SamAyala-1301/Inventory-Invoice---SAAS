import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework import authentication, exceptions
from .models import User, RefreshToken


class JWTAuthentication(authentication.BaseAuthentication):
    """
    JWT Authentication backend for Django REST Framework.
    Validates access tokens sent in Authorization header.
    """
    
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return None
        
        # Extract token from "Bearer <token>"
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            raise exceptions.AuthenticationFailed('Invalid authorization header format')
        
        token = parts[1]
        
        try:
            # Decode and validate token
            payload = decode_access_token(token)
            user_id = payload.get('user_id')
            
            if not user_id:
                raise exceptions.AuthenticationFailed('Invalid token payload')
            
            # Get user from database
            try:
                user = User.objects.get(id=user_id, is_active=True)
            except User.DoesNotExist:
                raise exceptions.AuthenticationFailed('User not found or inactive')
            
            return (user, token)
            
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Token validation failed: {str(e)}')


def generate_access_token(user):
    """
    Generate a short-lived JWT access token.
    
    Args:
        user: User instance
    
    Returns:
        str: JWT access token
    """
    payload = {
        'user_id': str(user.id),
        'email': user.email,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + settings.JWT_SETTINGS['ACCESS_TOKEN_LIFETIME'],
    }
    
    token = jwt.encode(
        payload,
        settings.JWT_SETTINGS['SECRET_KEY'],
        algorithm=settings.JWT_SETTINGS['ALGORITHM']
    )
    
    return token


def decode_access_token(token):
    """
    Decode and validate JWT access token.
    
    Args:
        token: JWT token string
    
    Returns:
        dict: Decoded token payload
    
    Raises:
        jwt.ExpiredSignatureError: If token has expired
        jwt.InvalidTokenError: If token is invalid
    """
    return jwt.decode(
        token,
        settings.JWT_SETTINGS['SECRET_KEY'],
        algorithms=[settings.JWT_SETTINGS['ALGORITHM']]
    )


def generate_refresh_token(user, request=None):
    """
    Generate a long-lived refresh token and store it in database.
    
    Args:
        user: User instance
        request: HTTP request object (optional, for tracking device info)
    
    Returns:
        RefreshToken: RefreshToken instance
    """
    import secrets
    
    # Generate random token
    token_string = secrets.token_urlsafe(32)
    
    # Get device info from request
    user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
    ip_address = get_client_ip(request) if request else None
    
    # Create refresh token in database
    refresh_token = RefreshToken.objects.create(
        user=user,
        token=token_string,
        expires_at=datetime.utcnow() + settings.JWT_SETTINGS['REFRESH_TOKEN_LIFETIME'],
        user_agent=user_agent[:500],  # Truncate if too long
        ip_address=ip_address
    )
    
    return refresh_token


def rotate_refresh_token(old_token_string, request=None):
    """
    Rotate refresh token - invalidate old one and create new one.
    This provides better security by limiting token lifetime.
    
    Args:
        old_token_string: The refresh token to rotate
        request: HTTP request object (optional)
    
    Returns:
        tuple: (access_token, new_refresh_token)
    
    Raises:
        exceptions.AuthenticationFailed: If token is invalid
    """
    try:
        # Get and validate old token
        old_token = RefreshToken.objects.get(token=old_token_string)
        
        if not old_token.is_valid():
            raise exceptions.AuthenticationFailed('Refresh token is invalid or expired')
        
        # Revoke old token
        old_token.revoke()
        
        # Generate new tokens
        access_token = generate_access_token(old_token.user)
        new_refresh_token = generate_refresh_token(old_token.user, request)
        
        return access_token, new_refresh_token
        
    except RefreshToken.DoesNotExist:
        raise exceptions.AuthenticationFailed('Refresh token not found')


def revoke_refresh_token(token_string):
    """
    Revoke a refresh token (e.g., on logout).
    
    Args:
        token_string: The refresh token to revoke
    """
    try:
        token = RefreshToken.objects.get(token=token_string)
        token.revoke()
    except RefreshToken.DoesNotExist:
        pass  # Token doesn't exist, nothing to revoke


def revoke_all_user_tokens(user):
    """
    Revoke all refresh tokens for a user (e.g., on password change).
    
    Args:
        user: User instance
    """
    RefreshToken.objects.filter(
        user=user,
        revoked_at__isnull=True
    ).update(revoked_at=datetime.utcnow())


def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip