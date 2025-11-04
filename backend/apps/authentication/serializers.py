from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, EmailVerificationToken, PasswordResetToken
from .backends import generate_access_token, generate_refresh_token
import secrets
from django.utils import timezone
from datetime import timedelta


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_verified', 'created_at']
        read_only_fields = ['id', 'email', 'is_verified', 'created_at']


class RegisterSerializer(serializers.Serializer):
    """Serializer for user registration"""
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    
    def validate_email(self, value):
        """Check if email already exists"""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()
    
    def validate(self, data):
        """Validate password match and strength"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        
        # Validate password strength
        try:
            validate_password(data['password'])
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        
        return data
    
    def create(self, validated_data):
        """Create new user and send verification email"""
        validated_data.pop('password_confirm')
        
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        # Create verification token
        token = secrets.token_urlsafe(32)
        EmailVerificationToken.objects.create(
            user=user,
            token=token,
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        # # Send verification email (via Celery task)
        # from .tasks import send_verification_email
        # send_verification_email.delay(user.id, token)
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    
    def validate(self, data):
        """Validate credentials and return tokens"""
        email = data.get('email', '').lower()
        password = data.get('password')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "Invalid credentials."})
        
        # Check if account is locked
        if user.is_locked():
            locked_until = user.locked_until.strftime('%Y-%m-%d %H:%M:%S')
            raise serializers.ValidationError({
                "detail": f"Account is locked due to too many failed login attempts. Try again after {locked_until}."
            })
        
        # Check password
        if not user.check_password(password):
            user.increment_failed_login()
            raise serializers.ValidationError({"detail": "Invalid credentials."})
        
        # Check if user is active
        if not user.is_active:
            raise serializers.ValidationError({"detail": "Account is disabled."})
        
        # Reset failed login attempts
        user.reset_failed_login()
        
        # Generate tokens
        request = self.context.get('request')
        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user, request)
        
        return {
            'user': user,
            'access_token': access_token,
            'refresh_token': refresh_token.token,
            'refresh_token_expires_at': refresh_token.expires_at
        }


class RefreshTokenSerializer(serializers.Serializer):
    """Serializer for refreshing access token"""
    
    refresh_token = serializers.CharField(required=True)
    
    def validate(self, data):
        """Validate refresh token and return new tokens"""
        from .backends import rotate_refresh_token
        from rest_framework.exceptions import AuthenticationFailed
        
        try:
            request = self.context.get('request')
            access_token, new_refresh_token = rotate_refresh_token(
                data['refresh_token'],
                request
            )
            
            return {
                'access_token': access_token,
                'refresh_token': new_refresh_token.token,
                'refresh_token_expires_at': new_refresh_token.expires_at
            }
        except AuthenticationFailed as e:
            raise serializers.ValidationError({"detail": str(e)})


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout"""
    
    refresh_token = serializers.CharField(required=True)
    
    def validate(self, data):
        """Revoke refresh token"""
        from .backends import revoke_refresh_token
        revoke_refresh_token(data['refresh_token'])
        return data


class VerifyEmailSerializer(serializers.Serializer):
    """Serializer for email verification"""
    
    token = serializers.CharField(required=True)
    
    def validate_token(self, value):
        """Validate and use verification token"""
        try:
            verification_token = EmailVerificationToken.objects.get(token=value)
            
            if not verification_token.is_valid():
                raise serializers.ValidationError("Verification token is invalid or expired.")
            
            # Mark user as verified
            user = verification_token.user
            user.is_verified = True
            user.save(update_fields=['is_verified'])
            
            # Mark token as used
            verification_token.mark_used()
            
            return value
            
        except EmailVerificationToken.DoesNotExist:
            raise serializers.ValidationError("Invalid verification token.")


class ForgotPasswordSerializer(serializers.Serializer):
    """Serializer for requesting password reset"""
    
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Check if user exists and send reset email"""
        try:
            user = User.objects.get(email=value.lower(), is_active=True)
            
            # Create password reset token
            token = secrets.token_urlsafe(32)
            PasswordResetToken.objects.create(
                user=user,
                token=token,
                expires_at=timezone.now() + timedelta(hours=1)
            )
            
            # Send reset email (via Celery task)
            from .tasks import send_password_reset_email
            send_password_reset_email.delay(user.id, token)
            
        except User.DoesNotExist:
            # Don't reveal if email exists or not (security)
            pass
        
        return value


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for resetting password with token"""
    
    token = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    def validate(self, data):
        """Validate passwords match and strength"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        
        # Validate password strength
        try:
            validate_password(data['password'])
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        
        return data
    
    def validate_token(self, value):
        """Validate reset token"""
        try:
            reset_token = PasswordResetToken.objects.get(token=value)
            
            if not reset_token.is_valid():
                raise serializers.ValidationError("Reset token is invalid or expired.")
            
            return value
            
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Invalid reset token.")
    
    def save(self):
        """Reset user password"""
        token = self.validated_data['token']
        password = self.validated_data['password']
        
        reset_token = PasswordResetToken.objects.get(token=token)
        user = reset_token.user
        
        # Set new password
        user.set_password(password)
        user.save()
        
        # Mark token as used
        reset_token.mark_used()
        
        # Revoke all existing refresh tokens for security
        from .backends import revoke_all_user_tokens
        revoke_all_user_tokens(user)
        
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password (authenticated user)"""
    
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, required=True)
    
    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    
    def validate(self, data):
        """Validate new passwords match and strength"""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Passwords do not match."})
        
        # Validate password strength
        try:
            validate_password(data['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})
        
        return data
    
    def save(self):
        """Change user password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        
        # Revoke all existing refresh tokens
        from .backends import revoke_all_user_tokens
        revoke_all_user_tokens(user)
        
        return user