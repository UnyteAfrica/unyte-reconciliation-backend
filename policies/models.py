from django.db import models


class Policies(models.Model):
    name = models.CharField(null=False, max_length=200)
    amount = models.CharField(null=False, max_length=200)
    sold = models.BooleanField(null=False, default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    device = models.OneToOneField("devices.Devices", on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'policy'
        verbose_name_plural = 'policies'
