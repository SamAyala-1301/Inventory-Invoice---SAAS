from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    RefreshTokenSerializer,
    LogoutSerializer,
    VerifyEmailSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    ChangePasswordSerializer,
    UserSerializer
)


@method_decorator(ratelimit(key='ip', rate='5/15m', method='POST'), name='post')
class RegisterView(APIView):
    """User registration endpoint"""
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: UserSerializer,
            400: OpenApiResponse(description='Validation error')
        },
        description='Register a new user account'
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response(
            {
                'message': 'Registration successful. Please check your email to verify your account.',
                'user': UserSerializer(user).data
            },
            status=status.HTTP_201_CREATED
        )


@method_decorator(ratelimit(key='ip', rate='5/15m', method='POST'), name='post')
class LoginView(APIView):
    """User login endpoint"""
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                description='Login successful',
                response={
                    'type': 'object',
                    'properties': {
                        'access_token': {'type': 'string'},
                        'refresh_token': {'type': 'string'},
                        'user': {'type': 'object'}
                    }
                }
            ),
            400: OpenApiResponse(description='Invalid credentials')
        },
        description='Login with email and password'
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        user = data.pop('user')
        
        return Response({
            'access_token': data['access_token'],
            'refresh_token': data['refresh_token'],
            'refresh_token_expires_at': data['refresh_token_expires_at'].isoformat(),
            'user': UserSerializer(user).data
        })


class RefreshTokenView(APIView):
    """Refresh access token using refresh token"""
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=RefreshTokenSerializer,
        responses={
            200: OpenApiResponse(
                description='Token refreshed successfully',
                response={
                    'type': 'object',
                    'properties': {
                        'access_token': {'type': 'string'},
                        'refresh_token': {'type': 'string'}
                    }
                }
            ),
            400: OpenApiResponse(description='Invalid or expired refresh token')
        },
        description='Get new access token using refresh token'
    )
    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        return Response({
            'access_token': data['access_token'],
            'refresh_token': data['refresh_token'],
            'refresh_token_expires_at': data['refresh_token_expires_at'].isoformat()
        })


class LogoutView(APIView):
    """User logout endpoint"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=LogoutSerializer,
        responses={
            200: OpenApiResponse(description='Logout successful'),
            400: OpenApiResponse(description='Invalid request')
        },
        description='Logout and revoke refresh token'
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response({
            'message': 'Logout successful'
        })


class VerifyEmailView(APIView):
    """Email verification endpoint"""
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=VerifyEmailSerializer,
        responses={
            200: OpenApiResponse(description='Email verified successfully'),
            400: OpenApiResponse(description='Invalid or expired token')
        },
        description='Verify email address using token'
    )
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response({
            'message': 'Email verified successfully'
        })


@method_decorator(ratelimit(key='ip', rate='3/1h', method='POST'), name='post')
class ForgotPasswordView(APIView):
    """Request password reset endpoint"""
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=ForgotPasswordSerializer,
        responses={
            200: OpenApiResponse(description='Password reset email sent if account exists'),
        },
        description='Request password reset link'
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Always return success to prevent email enumeration
        return Response({
            'message': 'If an account exists with this email, you will receive a password reset link.'
        })


class ResetPasswordView(APIView):
    """Reset password with token endpoint"""
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=ResetPasswordSerializer,
        responses={
            200: OpenApiResponse(description='Password reset successful'),
            400: OpenApiResponse(description='Invalid or expired token')
        },
        description='Reset password using token from email'
    )
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'Password reset successful. Please login with your new password.'
        })


class ChangePasswordView(APIView):
    """Change password (authenticated user)"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(description='Password changed successfully'),
            400: OpenApiResponse(description='Invalid old password or validation error')
        },
        description='Change password for authenticated user'
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'Password changed successfully. Please login again with your new password.'
        })


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user
    
    @extend_schema(
        responses={200: UserSerializer},
        description='Get current user profile'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        request=UserSerializer,
        responses={200: UserSerializer},
        description='Update current user profile'
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)