from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Agent
from .models import AgentProfile


@receiver(post_save, sender=Agent)
def create_profile(instance, created, **kwargs):
    if created:
        AgentProfile.objects.create(agent=instance)


@receiver(post_save, sender=Agent)
def create_profile(instance, **kwargs):
    instance.agentprofile.save()
