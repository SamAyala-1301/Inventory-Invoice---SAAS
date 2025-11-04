from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrganizationViewSet,
    AcceptInvitationView,
    RoleListView,
    PermissionListView
)

router = DefaultRouter()
router.register('', OrganizationViewSet, basename='organization')

urlpatterns = [
    path('invitations/accept/', AcceptInvitationView.as_view(), name='accept-invitation'),
    path('roles/', RoleListView.as_view(), name='role-list'),
    path('permissions/', PermissionListView.as_view(), name='permission-list'),
    path('', include(router.urls)),
]