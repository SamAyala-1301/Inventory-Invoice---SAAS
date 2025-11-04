import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.core.validators import EmailValidator


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model with email as username"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        max_length=255,
        unique=True,
        validators=[EmailValidator()],
        db_index=True
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email
    
    def is_locked(self):
        """Check if account is locked due to failed login attempts"""
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False
    
    def increment_failed_login(self):
        """Increment failed login attempts and lock if threshold reached"""
        self.failed_login_attempts += 1
        
        # Lock account after 10 failed attempts for 30 minutes
        if self.failed_login_attempts >= 10:
            self.locked_until = timezone.now() + timezone.timedelta(minutes=30)
        
        self.save(update_fields=['failed_login_attempts', 'locked_until'])
    
    def reset_failed_login(self):
        """Reset failed login attempts after successful login"""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.last_login_at = timezone.now()
        self.save(update_fields=['failed_login_attempts', 'locked_until', 'last_login_at'])


class RefreshToken(models.Model):
    """Store refresh tokens for JWT authentication"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refresh_tokens')
    token = models.CharField(max_length=500, unique=True, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    
    # Track which device/client the token is for
    user_agent = models.CharField(max_length=500, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = 'refresh_tokens'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'revoked_at']),
            models.Index(fields=['expires_at', 'revoked_at']),
        ]
    
    def __str__(self):
        return f"RefreshToken for {self.user.email}"
    
    def is_valid(self):
        """Check if token is still valid"""
        if self.revoked_at:
            return False
        if self.expires_at < timezone.now():
            return False
        return True
    
    def revoke(self):
        """Revoke the token"""
        self.revoked_at = timezone.now()
        self.save(update_fields=['revoked_at'])


class EmailVerificationToken(models.Model):
    """Tokens for email verification"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.CharField(max_length=100, unique=True, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'email_verification_tokens'
        ordering = ['-created_at']
    
    def is_valid(self):
        """Check if token is still valid"""
        if self.used_at:
            return False
        if self.expires_at < timezone.now():
            return False
        return True
    
    def mark_used(self):
        """Mark token as used"""
        self.used_at = timezone.now()
        self.save(update_fields=['used_at'])


class PasswordResetToken(models.Model):
    """Tokens for password reset"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=100, unique=True, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'password_reset_tokens'
        ordering = ['-created_at']
    
    def is_valid(self):
        """Check if token is still valid"""
        if self.used_at:
            return False
        if self.expires_at < timezone.now():
            return False
        return True
    
    def mark_used(self):
        """Mark token as used"""
        self.used_at = timezone.now()
        self.save(update_fields=['used_at'])