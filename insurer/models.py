from django.db import models
from user.models import BaseUser
from agents.models import Agent


class Insurer(BaseUser):
    location = models.CharField(null=True, blank=True, max_length=200)
    # agents = models.ForeignKey("agents.Agent", on_delete=models.CASCADE)
    # policies = models.ForeignKey()

    def __str__(self):
        return self.username.upper()
