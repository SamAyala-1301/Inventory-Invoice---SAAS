# # from celery import shared_task
# from django.core.mail import send_mail
# from django.conf import settings
# from django.template.loader import render_to_string
# import logging

# logger = logging.getLogger(__name__)


# @shared_task
# def send_verification_email(user_id, token):
#     """Send email verification link to user"""
#     from .models import User
    
#     try:
#         user = User.objects.get(id=user_id)
#         verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        
#         subject = 'Verify your email address'
#         message = f"""
#         Hi {user.first_name or user.email},
        
#         Thank you for registering! Please verify your email address by clicking the link below:
        
#         {verification_link}
        
#         This link will expire in 24 hours.
        
#         If you didn't create this account, you can safely ignore this email.
        
#         Best regards,
#         Inventory SaaS Team
#         """
        
#         send_mail(
#             subject=subject,
#             message=message,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[user.email],
#             fail_silently=False,
#         )
        
#         logger.info(f"Verification email sent to {user.email}")
        
#     except User.DoesNotExist:
#         logger.error(f"User {user_id} not found for verification email")
#     except Exception as e:
#         logger.error(f"Error sending verification email: {str(e)}")
#         raise


# @shared_task
# def send_password_reset_email(user_id, token):
#     """Send password reset link to user"""
#     from .models import User
    
#     try:
#         user = User.objects.get(id=user_id)
#         reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        
#         subject = 'Reset your password'
#         message = f"""
#         Hi {user.first_name or user.email},
        
#         You requested to reset your password. Click the link below to set a new password:
        
#         {reset_link}
        
#         This link will expire in 1 hour.
        
#         If you didn't request this, you can safely ignore this email.
        
#         Best regards,
#         Inventory SaaS Team
#         """
        
#         send_mail(
#             subject=subject,
#             message=message,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[user.email],
#             fail_silently=False,
#         )
        
#         logger.info(f"Password reset email sent to {user.email}")
        
#     except User.DoesNotExist:
#         logger.error(f"User {user_id} not found for password reset email")
#     except Exception as e:
#         logger.error(f"Error sending password reset email: {str(e)}")
#         raise


# @shared_task
# def cleanup_expired_tokens():
#     """Periodic task to clean up expired tokens"""
#     from .models import EmailVerificationToken, PasswordResetToken, RefreshToken
#     from django.utils import timezone
    
#     try:
#         # Delete expired verification tokens
#         expired_verification = EmailVerificationToken.objects.filter(
#             expires_at__lt=timezone.now(),
#             used_at__isnull=True
#         ).delete()
        
#         # Delete expired password reset tokens
#         expired_reset = PasswordResetToken.objects.filter(
#             expires_at__lt=timezone.now(),
#             used_at__isnull=True
#         ).delete()
        
#         # Delete expired refresh tokens
#         expired_refresh = RefreshToken.objects.filter(
#             expires_at__lt=timezone.now()
#         ).delete()
        
#         logger.info(
#             f"Cleaned up tokens - "
#             f"Verification: {expired_verification[0]}, "
#             f"Reset: {expired_reset[0]}, "
#             f"Refresh: {expired_refresh[0]}"
#         )
        
#     except Exception as e:
#         logger.error(f"Error cleaning up expired tokens: {str(e)}")
#         raise