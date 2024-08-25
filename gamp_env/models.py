from django.db import models


class GampArbitraryUser(models.Model):
    uuid = models.UUIDField(null=False)
    first_name = models.CharField(max_length=70,
                                  null=False,
                                  blank=False,
                                  help_text="First name of gamp customer")
    last_name = models.CharField(max_length=70,
                                 null=False,
                                 blank=False,
                                 help_text="Last name of gamp customer")
    phone_number = models.CharField(max_length=70,
                                    null=False,
                                    blank=False,
                                    help_text="Phone number customer")
    email = models.EmailField(null=False,
                              blank=False,
                              help_text="Email of gamp customer")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class GampArbitraryDevice(models.Model):
    IPHONE = "iPhone"
    SAMSUNG = "Samsung"

    DEVICE_TYPES = [
        (IPHONE, "iPhone"),
        (SAMSUNG, "Samsung")
    ]

    device_id = models.UUIDField(null=False,
                                 help_text="Device id")
    device_type = models.CharField(max_length=100,
                                   null=False,
                                   blank=False,
                                   choices=DEVICE_TYPES,
                                   help_text="Type of device")
    model = models.CharField(max_length=100,
                             null=False,
                             blank=False,
                             help_text="Model of device")
    customer = models.ForeignKey(GampArbitraryUser,
                                 on_delete=models.CASCADE,
                                 help_text="Customer who owns this device")

    def __str__(self):
        return f"{self.device_id}"


class GampArbitraryClaim(models.Model):
    APPROVED = "APPROVED"
    PENDING = "PENDING"
    DECLINED = "DECLINED"

    STATUS = [
        (APPROVED, "APPROVED"),
        (PENDING, "PENDING"),
        (DECLINED, "DECLINED")
    ]

    WATER = "My phone fell into water"
    CRACKED_SCREEN = "My phone's screen got cracked"
    BATTERY = "My phone's battery spoilt"

    ISSUES = [
        (WATER, "WATER"),
        (CRACKED_SCREEN, "CRACKED SCREEN"),
        (BATTERY, "My phone's battery spoilt"),
    ]

    claim_uuid = models.UUIDField(null=False,
                                  help_text="Claims id")
    customer = models.ForeignKey(GampArbitraryUser,
                                 null=False,
                                 on_delete=models.CASCADE,
                                 help_text="User initiating claim")
    device = models.ForeignKey(GampArbitraryDevice,
                               null=False,
                               on_delete=models.CASCADE,
                               help_text="Device user is trying to claim policy for")
    description = models.TextField(max_length=250,
                                   null=False,
                                   blank=False,
                                   help_text="Description text on what damage(s) occurred to user's device")

    issue = models.CharField(max_length=100,
                             null=False,
                             blank=False,
                             choices=ISSUES,
                             help_text="What issue occurred to the phone")
    address = models.CharField(max_length=244,
                               null=False,
                               blank=False,
                               help_text="User's address")
    technician_address = models.CharField(max_length=244,
                                          null=False,
                                          blank=False,
                                          help_text="Address of technician who will work on the phone")
    status = models.CharField(max_length=20,
                              null=False,
                              blank=False,
                              choices=STATUS,
                              default="PENDING",
                              help_text="Status of the claim filled")

    def __str__(self):
        return f"{self.claim_uuid}"


class GampArbitraryProduct(models.Model):
    product_uuid = models.UUIDField(null=False)
    product_name = models.CharField(max_length=100,
                                    null=False,
                                    blank=False,
                                    help_text="Type of the product")
    premium = models.CharField(max_length=100,
                               null=False,
                               blank=False,
                               help_text="Price of the product")
    flat_fee = models.BooleanField(null=False,
                                   default=True)

    def __str__(self):
        return self.product_name


class GampArbitraryPolicy(models.Model):
    policy_uuid = models.UUIDField(null=False)
    policy_name = models.CharField(null=False,
                                   blank=False,
                                   max_length=200,
                                   help_text="Name of policy")
    description = models.TextField(null=False,
                                   blank=False,
                                   max_length=250,
                                   help_text="Description of a policy")
    policy_type = models.CharField(null=False,
                                   blank=False,
                                   max_length=20,
                                   default="",
                                   choices=[],
                                   help_text="Types of available policies")
    insurer = models.CharField(null=False,
                               blank=False,
                               max_length=100,
                               help_text="Insurer that created the policy")

    def __str__(self):
        return self.policy_name


class GampPolicyProducts(models.Model):
    policy = models.ForeignKey(GampArbitraryPolicy,
                               on_delete=models.CASCADE,
                               help_text="Policy associated to a product")
    product = models.ForeignKey(GampArbitraryProduct,
                                on_delete=models.CASCADE,
                                help_text="Product(s) associated to a policy")

    def __str__(self):
        return f"{self.policy.policy_name}, {self.product.product_name}"
