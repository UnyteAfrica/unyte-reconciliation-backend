from django.db import models
from django_resized import ResizedImageField

from user.models import CustomUser
from policies.models import Policies


class Agent(CustomUser):
    otp = models.CharField(unique=True,
                           max_length=6,
                           blank=True,
                           null=True)
    otp_created_at = models.TimeField(blank=True,
                                      null=True)
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
                               null=True,
                               related_name="agent_policy")
    unyte_unique_agent_id = models.CharField(max_length=70,
                                             unique=True,
                                             null=False,
                                             blank=False)
    agent_gampID = models.CharField(null=True,
                                    blank=True,
                                    help_text='GAMP ID for users associated with GAMP')

    def __str__(self):
        return self.first_name.upper()

    def get_policies(self):
        policies = Policies.objects.filter(agentpolicy__agent=self)
        return policies

    def get_sold_policies(self):
        sold_policies = Policies.objects.filter(agentpolicy__agent=self, agentpolicy__is_sold=True)
        return sold_policies


class AgentProfile(models.Model):
    agent = models.OneToOneField(Agent, on_delete=models.CASCADE)
    profile_image = ResizedImageField(size=[400, 400], default='profile_pic/default.png', upload_to='profile_pic')

    def __str__(self):
        return f'{self.agent} Profile'
