from django.db import models
from django_resized import ResizedImageField
from django.conf import settings


class  Insurer(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
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
    unyte_unique_insurer_id = models.CharField(max_length=70,
                                               unique=True,
                                               null=False,
                                               blank=False)
    otp = models.CharField(unique=True,
                           max_length=6,
                           blank=True,
                           null=True)
    otp_created_at = models.TimeField(blank=True,
                                      null=True)

    class Meta:
        verbose_name = "INSURER"
        verbose_name_plural = "INSURERS"

    def __str__(self):
        return self.business_name


class InsurerProfile(models.Model):
    insurer = models.OneToOneField(Insurer, on_delete=models.CASCADE)
    profile_image = ResizedImageField(size=[400, 400], default='profile_pic/default.png', upload_to='profile_pic')

    class Meta:
        verbose_name = "INSURER PROFILE"
        verbose_name_plural = "INSURER PROFILES"

    def __str__(self):
        return f'{self.insurer} Profile'
