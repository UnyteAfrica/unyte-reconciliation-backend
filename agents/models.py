from django.db import models
from user.models import BaseUser


class Agent(BaseUser):
    insurance_company = models.OneToOneField("insurer.Insurer", on_delete=models.CASCADE)
    policy = models.ForeignKey("policies.Policies", on_delete=models.CASCADE)
    gampID = models.UUIDField()

    def __str__(self):
        return self.username.upper()
