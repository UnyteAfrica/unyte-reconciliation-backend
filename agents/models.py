from django.db import models
from django_resized import ResizedImageField

from user.models import CustomUser


class Agent(CustomUser):
    first_name = models.CharField(max_length=50,
                                  blank=False,
                                  null=False,
                                  help_text="Agent first name")
    last_name = models.CharField(max_length=50,
                                 blank=True,
                                 null=True,
                                 help_text="Agent middle name")
    middle_name = models.CharField(max_length=50,
                                   blank=False,
                                   null=False,
                                   help_text="Agent middle name")
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
    unyte_unique_agent_id = models.CharField(max_length=70,
                                             unique=True,
                                             null=False,
                                             blank=False)
    agent_gampID = models.CharField(null=True,
                                    blank=True,
                                    help_text='GAMP ID for users associated with GAMP')
    otp = models.CharField(unique=True,
                           max_length=6,
                           blank=True,
                           null=True)
    otp_created_at = models.TimeField(blank=True,
                                      null=True)

    class Meta:
        verbose_name = "AGENT"
        verbose_name_plural = "AGENTS"

    def __str__(self):
        return f"{self.first_name}: {self.affiliated_company.business_name}"


class AgentProfile(models.Model):
    agent = models.OneToOneField(Agent, on_delete=models.CASCADE)
    profile_image = ResizedImageField(size=[400, 400], default='profile_pic/default.png', upload_to='profile_pic')

    class Meta:
        verbose_name = "AGENT PROFILE"
        verbose_name_plural = "AGENT PROFILES"

    def __str__(self):
        return f'{self.agent} Profile'
