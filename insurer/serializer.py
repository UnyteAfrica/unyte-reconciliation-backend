from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from .utils import generate_otp
from rest_framework.exceptions import ValidationError
from datetime import datetime

from .models import Insurer


class CreateInsurerSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(max_length=50,
                                          required=True,
                                          help_text='Insurer business name',
                                          allow_blank=False,
                                          allow_null=False)
    admin_name = serializers.CharField(max_length=20,
                                       required=True,
                                       help_text='Insurer account admin (handler) name',
                                       allow_blank=False,
                                       allow_null=False)
    business_registration_number = serializers.CharField(max_length=50,
                                                         required=True,
                                                         help_text='Business registration number or Tax ID of insurer')
    email = serializers.EmailField()
    password = serializers.CharField(max_length=16,
                                     allow_null=False,
                                     allow_blank=False)
    insurer_gampID = serializers.CharField(allow_blank=True,
                                   allow_null=True)

    class Meta:
        model = Insurer
        fields = [
            'business_name',
            'admin_name',
            'business_registration_number',
            'email',
            'password',
            'insurer_gampID'
        ]

    def validate(self, attrs):
        insurer_gampID = attrs.get('insurer_gampID')
        admin_name = attrs.get('admin_name')
        business_reg_num = attrs.get('business_registration_number')

        if insurer_gampID == '':
            return attrs

        pattern = f'{admin_name}+{business_reg_num}@getgamp.com'

        if insurer_gampID != pattern:
            raise ValidationError("Invalid GampID")
        return attrs

    def create(self, validated_data):
        print(validated_data)
        user = Insurer.objects.create_user(**validated_data, otp=generate_otp(), otp_created_at=datetime.now().time())
        user.save()
        return user


class LoginInsurerSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=255)

    class Meta:
        model = Insurer
        fields = [
            'email',
            'password'
        ]


class OTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(required=False, max_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        if not Insurer.objects.filter(email=email).exists():
            raise ObjectDoesNotExist
        return attrs


class VerifyInsurerSerializer(serializers.Serializer):
    otp = serializers.CharField(required=False, max_length=6)


class SendNewOTPSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = Insurer
        fields = [
            'email'
        ]


class ForgotPasswordEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = Insurer
        fields = [
            'email'
        ]


class ForgotPasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=16)
    confirm_password = serializers.CharField(max_length=16)

    def check_passwords_equal(self) -> ValidationError:
        new_password = self.validated_data.get('new_password')
        confirm_password = self.validated_data.get('confirm_password')

        if new_password != confirm_password:
            return ValidationError("Password Mismatch")
