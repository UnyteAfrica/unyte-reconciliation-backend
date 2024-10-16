
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

from .models import Insurer, InsurerProfile

custom_user = get_user_model()


# @receiver(post_save, sender=Insurer)
# def send_verification_email(sender, instance, created, **kwargs,):
#     is_verified = instance.is_verified
#
#     if created:
#         return
#
#     if is_verified and kwargs.get('update_fields') is None:
#         try:
#             business_name = instance.business_name
#             email = instance.email
#             current_year = datetime.now().year
#             print(business_name)
#             context = {
#                 "business_name": business_name,
#                 "current_year": current_year
#             }
#             html_message = render_to_string("verification.html", context)
#             plain_message = strip_tags(html_message)
#
#             send_mail(
#                 subject='Verification email',
#                 message=plain_message,
#                 from_email=settings.EMAIL_HOST_USER,
#                 recipient_list=[settings.TO_EMAIL, email],
#                 html_message=html_message,
#             )
#
#             print("successfully sent verification email")
#
#         except Exception as e:
#             return e


@receiver(post_save, sender=Insurer)
def create_profile(instance, created, **kwargs):
    if created:
        InsurerProfile.objects.create(insurer=instance)


@receiver(post_save, sender=Insurer)
def save_profile(instance, **kwargs):
    instance.insurerprofile.save()
