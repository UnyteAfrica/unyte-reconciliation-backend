from django.db import models
from django.utils.translation import gettext as _


class Policies(models.Model):
    DEVICE_POLICY = 'device'

    POLICY_TYPES = (
        DEVICE_POLICY, _('Policy for Devices'),
    )

    insurer = models.ForeignKey("insurer.Insurer",
                                on_delete=models.CASCADE,
                                help_text="Insurer that create the policy")

    name = models.CharField(null=False,
                            blank=False,
                            unique=True,
                            max_length=200,
                            help_text="The name of the policy")
    policy_type = models.CharField(null=False,
                                   blank=False,
                                   max_length=50,
                                   default=DEVICE_POLICY,
                                   help_text="The class a policy falls under. For now, we only support Device Policies")
    amount = models.CharField(null=False,
                              blank=False,
                              max_length=200,
                              help_text="Amount policy should be sold at")
    valid_from = models.DateTimeField(null=False,
                                      blank=False,
                                      help_text="Date at which policy is valid from")
    valid_to = models.DateTimeField(null=False,
                                    blank=False,
                                    help_text="Policy Expiration date")
    created_at = models.DateTimeField(null=False,
                                      auto_now_add=True,
                                      help_text="Date policy was created")
    updated_at = models.DateTimeField(null=False,
                                      blank=False,
                                      auto_now=True,
                                      help_text="Date at which the policy was updated")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'policy'
        verbose_name_plural = 'policies'


class AgentPolicy(models.Model):
    agent = models.ForeignKey("agents.Agent", on_delete=models.CASCADE)
    policy = models.ForeignKey(Policies, on_delete=models.CASCADE)
    quantity_bought = models.IntegerField(null=False, blank=False, default=1)
    quantity_sold = models.IntegerField(null=False, blank=False, default=0)
    is_sold = models.BooleanField(default=False)

    class Meta:
        unique_together = ['agent', 'policy']
        verbose_name = 'agent policy'
        verbose_name_plural = 'agent policies'

    def __str__(self):
        return f'{self.agent} - {self.policy}'

    @staticmethod
    def can_sell_policy(policy: Policies = None, policy_list: list[Policies] = None) -> bool:
        # if policy is not None:
        #     valid_from = policy.valid_from.date()
        #     valid_to = policy.valid_to.date()
        #     if (valid_from - valid_to).days < 30:
        #         return False
        #     return True
        #
        # if policy_list is not None:
        #     for policy_ in policy_list:
        #         valid_from = policy_.valid_from.date()
        #         valid_to = policy_.valid_to.date()
        #
        #         if (valid_from - valid_to).days < 30:
        #             return False

        return True



