from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import Merchant, MerchantProfile


@receiver(post_save, sender=Merchant)
def create_merchant_profile(instance, created, **kwargs):
    if created:
        merchant_profile = MerchantProfile.objects.create(merchant=instance)
        merchant_profile.save()
