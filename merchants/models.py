import uuid

from django.db import models
from django.conf import settings


class Merchant(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=255,
        verbose_name='Business Name',
        help_text='The name of the business',
    )
    short_code = models.CharField(
        'Merchant Short code',
        max_length=10,
        help_text='Unique short code indentifier used internally to identify a merchant or distributor'
        'e.g. UBA-X224, GTB-3X2, KON-001, SLOT-001, WEMA-2286, etc.',
        unique=True,
        null=False,
        blank=False,
    )
    support_email = models.EmailField(
        'Support Email',
        default='',
        blank=True,
        help_text='The contact email address of the business, for support if any',
    )
    is_active = models.BooleanField(default=False, help_text='Designates if the merchant is active')
    verified = models.BooleanField(default=False, help_text='Designates if the merchant is verified')
    tax_identification_number = models.CharField(
        'TIN',
        null=True,
        blank=True,
        unique=True,
        max_length=40,
        help_text='Unique tax identification number issued by federal or inland revenue service',
    )
    registration_number = models.CharField(
        'Registration Number',
        max_length=40,
        null=True,
        blank=True,
        unique=True,
        help_text='Government-issued registration number with the CAC',
    )
    address = models.TextField(
        'Business Address',
        help_text='The physical address of the business',
        default='',
        blank=True,
    )
    kyc_verified = models.BooleanField(
        'KYC Verified',
        default=False,
        help_text='Designates if the business has been verified by the platform',
        blank=True,
    )
    tenant_id = models.UUIDField(
        'Tenant ID',
        help_text='Unique identifier for the merchant in the system',
        null=False,
        blank=False,
        unique=True,
        editable=False,
        default=uuid.uuid4,
    )
