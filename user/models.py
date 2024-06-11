from django.db import models
from django.contrib.auth.models import AbstractUser


class BaseUser(AbstractUser):
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=False)
    updated_at = models.DateTimeField(auto_now=True, blank=False)
    # profile_picture = models.ImageField()

    def __str__(self):
        return self.username

