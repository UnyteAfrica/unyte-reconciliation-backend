from django.db import models


class Devices(models.Model):
    name = models.CharField(blank=True, null=True,
                            max_length=200)
    policy = models.ForeignKey("policies.Policies",
                               related_name='device_policy',
                               null=True,
                               blank=True,
                               on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True,
                                      blank=True)
    updated_at = models.DateTimeField(auto_now=True,
                                      blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'device'
        verbose_name_plural = 'devices'
