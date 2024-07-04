# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Insurer
# from .models import InsurerProfile
#
#
# @receiver(post_save, sender=Insurer)
# def create_profile(instance, created, **kwargs):
#     if created:
#         InsurerProfile.objects.create(insurer=instance)
#
#
# @receiver(post_save, sender=Insurer)
# def create_profile(instance, **kwargs):
#     instance.insurerprofile.save()
