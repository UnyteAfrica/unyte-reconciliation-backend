from django.db import models


class Policies(models.Model):
    name = models.CharField(null=False, max_length=200)
    amount = models.CharField(null=False, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'policy'
        verbose_name_plural = 'policies'


class AgentPolicy(models.Model):
    agent = models.ForeignKey("agents.Agent", on_delete=models.CASCADE)
    policy = models.ForeignKey(Policies, on_delete=models.CASCADE)
    is_sold = models.BooleanField(default=False)

    class Meta:
        unique_together = ['agent', 'policy']
        verbose_name = 'agent policy'
        verbose_name_plural = 'agent policies'

    def __str__(self):
        return f'{self.agent} - {self.policy}'


class InsurerPolicy(models.Model):
    insurer = models.ForeignKey("insurer.Insurer", on_delete=models.CASCADE)
    policy = models.ForeignKey(Policies, on_delete=models.CASCADE)
    is_sold = models.BooleanField(default=False)

    class Meta:
        unique_together = ['insurer', 'policy']
        verbose_name = 'insurer policy'
        verbose_name_plural = 'insurer policies'

    def __str__(self):
        return f'{self.insurer} - {self.policy}'

