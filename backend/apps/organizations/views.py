from rest_framework import status, generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.core.permissions import IsOrganizationAdmin, IsOrganizationOwner
from .models import (
    Organization,
    OrganizationMember,
    OrganizationInvitation,
    Role,
    Permission
)
from .serializers import (
    OrganizationSerializer,
    OrganizationMemberSerializer,
    UpdateMemberRoleSerializer,
    InviteMemberSerializer,
    OrganizationInvitationSerializer,
    AcceptInvitationSerializer,
    RoleSerializer,
    PermissionSerializer
)


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing organizations.
    List: Get all organizations user belongs to
    Create: Create new organization (user becomes owner)
    Retrieve/Update: Get/Update organization details
    Delete: Soft delete organization (owner only)
    """
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only organizations the user belongs to"""
        return Organization.objects.filter(
            members__user=self.request.user,
            members__is_active=True,
            is_active=True
        ).distinct()
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsOrganizationAdmin()]
        elif self.action == 'destroy':
            return [IsAuthenticated(), IsOrganizationOwner()]
        return [IsAuthenticated()]
    
    @extend_schema(
        responses={200: OrganizationSerializer(many=True)},
        description='List all organizations user belongs to'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        request=OrganizationSerializer,
        responses={201: OrganizationSerializer},
        description='Create new organization (creator becomes owner)'
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        responses={200: OrganizationSerializer},
        description='Get organization details'
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        request=OrganizationSerializer,
        responses={200: OrganizationSerializer},
        description='Update organization (admin only)'
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        responses={204: None},
        description='Delete organization (owner only, soft delete)'
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @extend_schema(
        responses={200: OrganizationMemberSerializer(many=True)},
        description='List organization members'
    )
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """List all members of the organization"""
        organization = self.get_object()
        members = OrganizationMember.objects.filter(
            organization=organization,
            is_active=True
        ).select_related('user', 'role', 'invited_by')
        
        serializer = OrganizationMemberSerializer(members, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        request=InviteMemberSerializer,
        responses={201: OrganizationInvitationSerializer},
        description='Invite user to organization (admin only)'
    )
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated, IsOrganizationAdmin]
    )
    def invite(self, request, pk=None):
        """Invite a user to join the organization"""
        organization = self.get_object()
        
        serializer = InviteMemberSerializer(
            data=request.data,
            context={
                'request': request,
                'organization': organization
            }
        )
        serializer.is_valid(raise_exception=True)
        invitation = serializer.save()
        
        return Response(
            OrganizationInvitationSerializer(invitation).data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        responses={200: OrganizationInvitationSerializer(many=True)},
        description='List pending invitations (admin only)'
    )
    @action(
        detail=True,
        methods=['get'],
        permission_classes=[IsAuthenticated, IsOrganizationAdmin]
    )
    def invitations(self, request, pk=None):
        """List all pending invitations"""
        organization = self.get_object()
        invitations = OrganizationInvitation.objects.filter(
            organization=organization,
            is_active=True,
            accepted_at__isnull=True
        ).select_related('role', 'invited_by')
        
        serializer = OrganizationInvitationSerializer(invitations, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        request=UpdateMemberRoleSerializer,
        responses={200: OrganizationMemberSerializer},
        description='Update member role (admin only)'
    )
    @action(
        detail=True,
        methods=['patch'],
        url_path='members/(?P<member_id>[^/.]+)',
        permission_classes=[IsAuthenticated, IsOrganizationAdmin]
    )
    def update_member(self, request, pk=None, member_id=None):
        """Update a member's role"""
        organization = self.get_object()
        
        try:
            member = OrganizationMember.objects.get(
                id=member_id,
                organization=organization,
                is_active=True
            )
        except OrganizationMember.DoesNotExist:
            return Response(
                {'error': 'Member not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Prevent changing owner role
        if member.role.name == 'Owner':
            return Response(
                {'error': 'Cannot change owner role'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = UpdateMemberRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_role = serializer.validated_data['role_id']
        
        # Prevent setting owner role
        if new_role.name == 'Owner':
            return Response(
                {'error': 'Cannot assign owner role'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        member.role = new_role
        member.save()
        
        # Invalidate permission cache
        from apps.core.permissions import invalidate_permission_cache
        invalidate_permission_cache(member.user, organization)
        
        return Response(OrganizationMemberSerializer(member).data)
    
    @extend_schema(
        responses={204: None},
        description='Remove member from organization (admin only)'
    )
    @action(
        detail=True,
        methods=['delete'],
        url_path='members/(?P<member_id>[^/.]+)',
        permission_classes=[IsAuthenticated, IsOrganizationAdmin]
    )
    def remove_member(self, request, pk=None, member_id=None):
        """Remove a member from the organization"""
        organization = self.get_object()
        
        try:
            member = OrganizationMember.objects.get(
                id=member_id,
                organization=organization,
                is_active=True
            )
        except OrganizationMember.DoesNotExist:
            return Response(
                {'error': 'Member not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Prevent removing owner
        if member.role.name == 'Owner':
            return Response(
                {'error': 'Cannot remove organization owner'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prevent removing self
        if member.user == request.user:
            return Response(
                {'error': 'Cannot remove yourself. Transfer ownership or delete organization.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        member.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AcceptInvitationView(generics.CreateAPIView):
    """Accept organization invitation"""
    serializer_class = AcceptInvitationSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=AcceptInvitationSerializer,
        responses={200: OrganizationMemberSerializer},
        description='Accept organization invitation'
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        member = serializer.save()
        
        return Response(
            OrganizationMemberSerializer(member).data,
            status=status.HTTP_200_OK
        )


class RoleListView(generics.ListAPIView):
    """List all available roles"""
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    queryset = Role.objects.filter(is_active=True)
    
    @extend_schema(
        responses={200: RoleSerializer(many=True)},
        description='List all available roles'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PermissionListView(generics.ListAPIView):
    """List all available permissions"""
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    queryset = Permission.objects.filter(is_active=True)
    
    @extend_schema(
        responses={200: PermissionSerializer(many=True)},
        description='List all available permissions'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)