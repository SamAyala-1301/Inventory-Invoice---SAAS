# # from celery import shared_task
# from django.core.mail import send_mail
# from django.conf import settings
# import logging

# logger = logging.getLogger(__name__)


# @shared_task
# def send_invitation_email(invitation_id):
#     """Send organization invitation email"""
#     from .models import OrganizationInvitation
    
#     try:
#         invitation = OrganizationInvitation.objects.select_related(
#             'organization', 'role', 'invited_by'
#         ).get(id=invitation_id)
        
#         accept_link = f"{settings.FRONTEND_URL}/invitations/accept?token={invitation.token}"
        
#         subject = f"You've been invited to join {invitation.organization.name}"
#         message = f"""
#         Hi,
        
#         {invitation.invited_by.full_name} has invited you to join {invitation.organization.name} as a {invitation.role.name}.
        
#         Click the link below to accept the invitation:
        
#         {accept_link}
        
#         This invitation will expire on {invitation.expires_at.strftime('%B %d, %Y at %I:%M %p')}.
        
#         If you don't have an account yet, you'll be able to create one after clicking the link.
        
#         Best regards,
#         Inventory SaaS Team
#         """
        
#         send_mail(
#             subject=subject,
#             message=message,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[invitation.email],
#             fail_silently=False,
#         )
        
#         logger.info(f"Invitation email sent to {invitation.email}")
        
#     except OrganizationInvitation.DoesNotExist:
#         logger.error(f"Invitation {invitation_id} not found")
#     except Exception as e:
#         logger.error(f"Error sending invitation email: {str(e)}")
#         raise