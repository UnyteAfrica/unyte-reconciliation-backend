from django.db import models
from django.contrib.auth.models import AbstractUser


class BaseUser(AbstractUser):
    created_at = models.DateTimeField(auto_now_add=True, blank=False)
    updated_at = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self):
        return self.username

