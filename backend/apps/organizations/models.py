from django.db import models
from apps.core.models import BaseModel
from apps.authentication.models import User


class Organization(BaseModel):
    """Organization/Tenant model"""
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    description = models.TextField(blank=True)
    
    # Contact information
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    
    # Address
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Settings
    currency = models.CharField(max_length=3, default='USD')
    timezone = models.CharField(max_length=50, default='UTC')
    
    class Meta:
        db_table = 'organizations'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Role(BaseModel):
    """Role definition for RBAC"""
    
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    level = models.IntegerField(
        default=0,
        help_text='Role hierarchy level (higher = more permissions)'
    )
    
    class Meta:
        db_table = 'roles'
        ordering = ['-level', 'name']
    
    def __str__(self):
        return self.name


class Permission(BaseModel):
    """Permission definition"""
    
    code = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, default='general')
    
    class Meta:
        db_table = 'permissions'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class RolePermission(BaseModel):
    """Many-to-many relationship between roles and permissions"""
    
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='role_permissions'
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='role_permissions'
    )
    
    class Meta:
        db_table = 'role_permissions'
        unique_together = ['role', 'permission']
        indexes = [
            models.Index(fields=['role', 'permission']),
        ]
    
    def __str__(self):
        return f"{self.role.name} - {self.permission.code}"


# Add ManyToMany relationship through RolePermission
Role.permissions = models.ManyToManyField(
    Permission,
    through=RolePermission,
    related_name='roles'
)


class OrganizationMember(BaseModel):
    """User membership in an organization with role"""
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='members'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organization_memberships'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name='members'
    )
    
    # Invitation tracking
    invited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invited_members'
    )
    invited_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'organization_members'
        unique_together = ['organization', 'user']
        indexes = [
            models.Index(fields=['organization', 'user']),
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.organization.name} ({self.role.name})"


class OrganizationInvitation(BaseModel):
    """Pending invitations to join an organization"""
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='invitations'
    )
    email = models.EmailField(db_index=True)
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name='invitations'
    )
    token = models.CharField(max_length=100, unique=True, db_index=True)
    
    invited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_invitations'
    )
    
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'organization_invitations'
        unique_together = ['organization', 'email']
        indexes = [
            models.Index(fields=['email', 'is_active']),
            models.Index(fields=['token', 'expires_at']),
        ]
    
    def __str__(self):
        return f"Invitation for {self.email} to {self.organization.name}"
    
    def is_valid(self):
        """Check if invitation is still valid"""
        from django.utils import timezone
        if self.accepted_at:
            return False
        if self.expires_at < timezone.now():
            return False
        if not self.is_active:
            return False
        return True