from django.db import transaction, IntegrityError
from django.contrib.auth import get_user_model

from rest_framework import serializers

from merchants.models import Merchant

class MerchantSerializer(serializers.ModelSerializer):
    business_email = serializers.ReadOnlyField(source='user.email')
    class Meta:
        model = Merchant
        fields = (
            'id',
            'name',
            'address',
            'verified',
            'tenant_id',
            'short_code',
            'kyc_verified',
            'support_email',
            'business_email',
            'registration_number',
            'tax_identification_number',
        )

class CreateMerchantSerializer(serializers.ModelSerializer):
    email_address = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = Merchant
        fields = (
            'name',
            'address',
            'verified',
            'tenant_id',
            'password',
            'short_code',
            'kyc_verified',
            'email_address',
            'support_email',
            'registration_number',
            'tax_identification_number',
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'email_address': {'write_only': True},
        }
        read_only_fields = ('tenant_id',)

    @transaction.atomic
    def create(self, validated_data):
        user_model = get_user_model()
        try:
            user = user_model.objects.create(
                email=validated_data.pop('email_address'),
                password=validated_data.pop('password'),
                is_merchant=True,
            )
        except IntegrityError:
            raise serializers.ValidationError(detail='user with this email already exists', code='duplicate_email')

        return Merchant.objects.create(user=user, **validated_data)
