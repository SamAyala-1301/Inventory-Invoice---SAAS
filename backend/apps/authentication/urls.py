from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    RefreshTokenView,
    LogoutView,
    VerifyEmailView,
    ForgotPasswordView,
    ResetPasswordView,
    ChangePasswordView,
    UserProfileView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh-token'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]