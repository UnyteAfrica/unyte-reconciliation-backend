from django.db import models
from django.conf import settings

from policies.models import Policies
from user.models import CustomUser


class Insurer(CustomUser):
    otp = models.CharField(unique=True,
                           max_length=6,
                           blank=True,
                           null=True)
    otp_created_at = models.TimeField(blank=True,
                                      null=True)
    business_name = models.CharField(unique=True,
                                     max_length=50,
                                     null=False,
                                     blank=False,
                                     help_text='Business name of insurer')
    admin_name = models.CharField(max_length=20,
                                  null=False,
                                  blank=False,
                                  help_text='Contact name of admin of insurer account')
    business_registration_number = models.CharField(unique=True,
                                                    max_length=50,
                                                    null=False,
                                                    blank=False,
                                                    help_text='Business registration number of Tax ID of insurer')
    insurer_gampID = models.CharField(null=True,
                                      blank=True,
                                      help_text='GAMP ID for users associated with GAMP')
    policies = models.ForeignKey("policies.Policies",
                                 related_name="insurer_policy",
                                 null=True,
                                 blank=True,
                                 on_delete=models.CASCADE)
    unyte_unique_insurer_id = models.CharField(max_length=70,
                                               unique=True,
                                               null=False,
                                               blank=False)

    def __str__(self):
        return self.business_name

    def get_policies(self):
        policies = Policies.objects.filter(insurerpolicy__insurer=self)
        return policies

    def get_sold_policies(self):
        sold_policies = Policies.objects.filter(insurerpolicy__insurer=self, insurerpolicy__is_sold=True)
        return sold_policies

# class InsurerProfile(models.Model):
#     insurer = models.OneToOneField(Insurer, on_delete=models.CASCADE)
#     profile_image = models.ImageField(default='default.png', upload_to=f'profile_pic')
#
#     def __str__(self):
#         return f'{self.insurer} Profile'
