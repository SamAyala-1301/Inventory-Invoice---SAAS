from rest_framework import serializers
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta
import secrets

from .models import (
    Organization,
    OrganizationMember,
    OrganizationInvitation,
    Role,
    Permission
)
from apps.authentication.serializers import UserSerializer


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for Organization"""
    
    member_count = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'description',
            'email', 'phone', 'website',
            'address_line1', 'address_line2', 'city', 'state',
            'postal_code', 'country',
            'currency', 'timezone',
            'member_count', 'user_role',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_member_count(self, obj):
        return obj.members.filter(is_active=True).count()
    
    def get_user_role(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                member = OrganizationMember.objects.get(
                    organization=obj,
                    user=request.user,
                    is_active=True
                )
                return member.role.name
            except OrganizationMember.DoesNotExist:
                return None
        return None
    
    def create(self, validated_data):
        # Generate unique slug
        slug = slugify(validated_data['name'])
        original_slug = slug
        counter = 1
        
        while Organization.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        validated_data['slug'] = slug
        organization = Organization.objects.create(**validated_data)
        
        # Add creator as owner
        user = self.context['request'].user
        owner_role = Role.objects.get(name='Owner')
        OrganizationMember.objects.create(
            organization=organization,
            user=user,
            role=owner_role
        )
        
        return organization


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role"""
    
    permission_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'level', 'permission_count']
        read_only_fields = ['id']
    
    def get_permission_count(self, obj):
        return obj.permissions.filter(is_active=True).count()


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for Permission"""
    
    class Meta:
        model = Permission
        fields = ['id', 'code', 'name', 'description', 'category']
        read_only_fields = ['id']


class OrganizationMemberSerializer(serializers.ModelSerializer):
    """Serializer for Organization Member"""
    
    user = UserSerializer(read_only=True)
    role = RoleSerializer(read_only=True)
    invited_by = UserSerializer(read_only=True)
    
    class Meta:
        model = OrganizationMember
        fields = [
            'id', 'user', 'role', 'invited_by',
            'invited_at', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'invited_at', 'created_at']


class UpdateMemberRoleSerializer(serializers.Serializer):
    """Serializer for updating member role"""
    
    role_id = serializers.UUIDField(required=True)
    
    def validate_role_id(self, value):
        try:
            role = Role.objects.get(id=value, is_active=True)
            return role
        except Role.DoesNotExist:
            raise serializers.ValidationError("Invalid role ID")


class InviteMemberSerializer(serializers.Serializer):
    """Serializer for inviting member to organization"""
    
    email = serializers.EmailField(required=True)
    role_id = serializers.UUIDField(required=True)
    
    def validate_email(self, value):
        return value.lower()
    
    def validate_role_id(self, value):
        try:
            role = Role.objects.get(id=value, is_active=True)
            
            # Prevent inviting as Owner (only one owner per org)
            if role.name == 'Owner':
                raise serializers.ValidationError("Cannot invite users as Owner")
            
            return role
        except Role.DoesNotExist:
            raise serializers.ValidationError("Invalid role ID")
    
    def validate(self, data):
        organization = self.context['organization']
        email = data['email']
        
        # Check if user is already a member
        from apps.authentication.models import User
        try:
            user = User.objects.get(email=email)
            if OrganizationMember.objects.filter(
                organization=organization,
                user=user,
                is_active=True
            ).exists():
                raise serializers.ValidationError({
                    "email": "User is already a member of this organization"
                })
        except User.DoesNotExist:
            pass
        
        # Check for existing pending invitation
        if OrganizationInvitation.objects.filter(
            organization=organization,
            email=email,
            is_active=True,
            accepted_at__isnull=True,
            expires_at__gt=timezone.now()
        ).exists():
            raise serializers.ValidationError({
                "email": "An invitation has already been sent to this email"
            })
        
        return data
    
    def save(self):
        organization = self.context['organization']
        invited_by = self.context['request'].user
        
        email = self.validated_data['email']
        role = self.validated_data['role_id']
        
        # Create invitation
        token = secrets.token_urlsafe(32)
        invitation = OrganizationInvitation.objects.create(
            organization=organization,
            email=email,
            role=role,
            token=token,
            invited_by=invited_by,
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        # Send invitation email
        from .tasks import send_invitation_email
        send_invitation_email.delay(invitation.id)
        
        return invitation


class OrganizationInvitationSerializer(serializers.ModelSerializer):
    """Serializer for Organization Invitation"""
    
    organization = OrganizationSerializer(read_only=True)
    role = RoleSerializer(read_only=True)
    invited_by = UserSerializer(read_only=True)
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = OrganizationInvitation
        fields = [
            'id', 'organization', 'email', 'role',
            'invited_by', 'expires_at', 'accepted_at',
            'is_valid', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_is_valid(self, obj):
        return obj.is_valid()


class AcceptInvitationSerializer(serializers.Serializer):
    """Serializer for accepting organization invitation"""
    
    token = serializers.CharField(required=True)
    
    def validate_token(self, value):
        try:
            invitation = OrganizationInvitation.objects.select_related(
                'organization', 'role'
            ).get(token=value)
            
            if not invitation.is_valid():
                raise serializers.ValidationError(
                    "Invitation is invalid or has expired"
                )
            
            return invitation
        except OrganizationInvitation.DoesNotExist:
            raise serializers.ValidationError("Invalid invitation token")
    
    def save(self):
        invitation = self.validated_data['token']
        user = self.context['request'].user
        
        # Check if user email matches invitation
        if user.email != invitation.email:
            raise serializers.ValidationError(
                "This invitation is for a different email address"
            )
        
        # Create organization membership
        member = OrganizationMember.objects.create(
            organization=invitation.organization,
            user=user,
            role=invitation.role,
            invited_by=invitation.invited_by
        )
        
        # Mark invitation as accepted
        invitation.accepted_at = timezone.now()
        invitation.is_active = False
        invitation.save()
        
        return member