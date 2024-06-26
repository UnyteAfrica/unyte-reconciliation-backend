from django.db import models
from user.models import CustomUser


class Agent(CustomUser):
    home_address = models.CharField(unique=True,
                                    max_length=255,
                                    null=False,
                                    blank=False,
                                    help_text='Agent home address')
    bvn = models.CharField(unique=True,
                           max_length=11,
                           null=False,
                           blank=False,
                           help_text='Agent BVN')
    bank_account = models.CharField(unique=True,
                                    max_length=10,
                                    null=False,
                                    blank=False,
                                    help_text='Agent Bank account')
    affiliated_company = models.ForeignKey("insurer.Insurer",
                                           on_delete=models.CASCADE,
                                           null=False,
                                           blank=True)
    policy = models.ForeignKey("policies.Policies",
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    agent_gampID = models.CharField(null=True,
                                    blank=True,
                                    help_text='GAMP ID for users associated with GAMP')

    def __str__(self):
        return self.first_name.upper()
