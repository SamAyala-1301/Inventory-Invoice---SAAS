import uuid
from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """
    Abstract base model with common fields for all models.
    Provides UUID primary key, timestamps, and soft delete functionality.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def soft_delete(self):
        """Soft delete the instance"""
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])

    def restore(self):
        """Restore soft deleted instance"""
        self.is_active = True
        self.save(update_fields=['is_active', 'updated_at'])


class TenantAwareModel(BaseModel):
    """
    Abstract base model for all tenant-scoped models.
    Automatically filters queries by organization context.
    """
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='%(class)s_set',
        db_index=True
    )

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['organization', 'id']),
            models.Index(fields=['organization', 'created_at']),
        ]

    def save(self, *args, **kwargs):
        # Ensure organization is set from request context if available
        if not self.organization_id:
            from .middleware import get_current_organization
            org = get_current_organization()
            if org:
                self.organization = org
        super().save(*args, **kwargs)