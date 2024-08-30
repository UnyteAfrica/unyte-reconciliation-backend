from django.db import models
from django.utils.translation import gettext as _


class Policies(models.Model):
    POLICY_CATEGORY = [
        ('LAUNCH', 'LAUNCH'),
        ('CREDIT LIFE', 'CREDIT LIFE'),
        ('DEVICE PROTECTION', 'DEVICE PROTECTION'),
        ('TRAVEL COVER', 'TRAVEL COVER'),
        ('HEALTH', 'HEALTH'),
        ('MOTOR REGISTRATION', 'MOTOR REGISTRATION'),
        ('STUDENT PROTECTION', 'STUDENT PROTECTION'),
        ('LOGISTICS', 'LOGISTICS'),
        ('CARD PROTECTION', 'CARD PROTECTION')
    ]
    insurer = models.ForeignKey("insurer.Insurer",
                                on_delete=models.CASCADE,
                                help_text="Insurer that create the policy")

    name = models.CharField(null=False,
                            blank=False,
                            max_length=200,
                            help_text="The name of the policy")
    policy_category = models.CharField(null=False,
                                       blank=False,
                                       max_length=50,
                                       choices=POLICY_CATEGORY,
                                       help_text="The class a policy falls under")
    valid_from = models.DateTimeField(null=False,
                                      blank=False,
                                      help_text="Date at which policy is valid from")
    valid_to = models.DateTimeField(null=False,
                                    blank=False,
                                    help_text="Policy Expiration date")

    def __str__(self):
        return f"{self.insurer.business_name} - {self.name}"

    class Meta:
        verbose_name = 'policy'
        verbose_name_plural = 'policies'


class PolicyProductType(models.Model):
    policy = models.ForeignKey(Policies,
                               on_delete=models.CASCADE,
                               help_text='Policy with product(s)')
    name = models.CharField(null=False,
                            blank=False,
                            unique=True,
                            max_length=200,
                            help_text="The name of the product")
    premium = models.CharField(null=False,
                               blank=False,
                               max_length=200,
                               help_text="Amount policy should be sold at")
    flat_fee = models.CharField(max_length=3,
                                choices=[('YES', 'Yes'), ('NO', 'No')],
                                help_text='Flat fee for the policy')
    broker_commission = models.DecimalField(max_digits=5,
                                            decimal_places=2,
                                            help_text='commission attached to the product')

    def __str__(self):
        return f"{self.policy.name} - {self.name}"


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
