import os

import requests as r
from dotenv import find_dotenv, load_dotenv

from django.db import IntegrityError, transaction
from django.forms import ValidationError
from django.contrib.auth import get_user_model

from rest_framework import serializers

from merchants.models import Merchant

load_dotenv(find_dotenv())

SUPERPOOL_BACKEND_URL = os.getenv('SUPERPOOL_BACKEND_URL')
SUPERPOOL_API_KEY = os.getenv('SUPERPOOL_API_KEY')

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

    def create_merchant_on_superpool(self, validated_data: dict) -> dict:
        """
        Create merchants on Superpool
        """
        company_name = validated_data.get('name')
        business_email = validated_data.get('email_address')
        support_email = validated_data.get('support_email')
        endpoint = 'merchants/'
        url = f'{SUPERPOOL_BACKEND_URL}/{endpoint}'
        response = r.post(  # noqa: S113
            url=url,
            data={
                'company_name': company_name,
                'business_email': business_email,
                'support_email': support_email
            },
            headers={
                'HTTP_X_BACKEND_API_KEY': SUPERPOOL_API_KEY
            }
        )

        if response.status_code != 201:
            raise ValidationError('Could not create Merchant on Superpool')
        return response.json()


    @transaction.atomic
    def create(self, validated_data):
        user_model = get_user_model()
        try:
            user = user_model.objects.create_user(
                email=validated_data.get('email_address'),
                password=validated_data.get('password'),
                is_merchant=True,
            )
            user.save()
            superpool_merchant = self.create_merchant_on_superpool(validated_data)
            superpool_merchant_tenant_id = superpool_merchant.get('data').get('tenant_id')
            validated_data['tenant_id'] = superpool_merchant_tenant_id
        except IntegrityError:
            raise serializers.ValidationError(detail='user with this email already exists', code='duplicate_email')  # noqa: B904

        validated_data.pop('email_address')
        validated_data.pop('password')

        return Merchant.objects.create(user=user, **validated_data)
