from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from .utils import generate_otp, CustomValidationError, generate_unyte_unique_insurer_id
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from datetime import datetime

from .models import Insurer, InsurerProfile
from policies.models import Policies
from agents.models import Agent

custom_user = get_user_model()


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
    business_registration_number = serializers.CharField(max_length=8,
                                                         min_length=8,
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
        business_name = attrs.get('business_name')
        email = attrs.get('email')

        if insurer_gampID == '':
            if Insurer.objects.filter(email=email).exists():
                raise CustomValidationError({"error": "Email already exists"})

            if custom_user.objects.filter(email=email).exists():
                raise CustomValidationError({"error": "Email already exists"})

            if Insurer.objects.filter(business_registration_number=business_reg_num).exists():
                raise CustomValidationError({"error": "Business Registration number already exists"})

            if Insurer.objects.filter(business_name=business_name).exists():
                raise CustomValidationError({"error": "Business Name  already exists"})

            return attrs

        else:
            if Insurer.objects.filter(insurer_gampID=insurer_gampID).exists():
                raise CustomValidationError({"error": "GampID already exists"})

            if Insurer.objects.filter(email=email).exists():
                raise CustomValidationError({"error": "Email already exists"})

            if custom_user.objects.filter(email=email).exists():
                raise CustomValidationError({"error": "Email already exists"})

            if Insurer.objects.filter(business_registration_number=business_reg_num).exists():
                raise CustomValidationError({"error": "Business Registration number already exists"})

            if Insurer.objects.filter(business_name=business_name).exists():
                raise CustomValidationError({"error": "Business Name  already exists"})

        pattern = f'{admin_name}+{business_reg_num}@getgamp.com'

        if insurer_gampID != pattern:
            raise CustomValidationError({"error": "Invalid GampID"})

        return attrs

    def create(self, validated_data):
        business_name = validated_data.get('business_name')
        business_reg_num = validated_data.get('business_registration_number')
        unyte_unique_insurer_id = generate_unyte_unique_insurer_id(business_name, business_reg_num)
        user = Insurer.objects.create_user(**validated_data, unyte_unique_insurer_id=unyte_unique_insurer_id,
                                           otp=generate_otp(), otp_created_at=datetime.now().time())
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


class ValidateRefreshToken(serializers.Serializer):
    refresh_token = serializers.CharField()


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

    def validate(self, attrs):
        insurer_email = attrs.get('email')
        if not Insurer.objects.filter(email=insurer_email).exists():
            message = {
                "error": "This email does not exist"
            }
            raise ValidationError(message)
        return attrs


class ForgotPasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=16)
    token = serializers.CharField(min_length=1)
    id_base64 = serializers.CharField(min_length=1)
    confirm_password = serializers.CharField(max_length=16)

    class Meta:
        fields = [
            'new_password',
            'confirm_password',
            'token',
            'id_base64'
        ]

    def validate(self, attrs):
        try:
            token = attrs.get('token')
            id_base64 = attrs.get('id_base64')
            new_password = attrs.get('new_password')
            confirm_password = attrs.get('confirm_password')

            insurer_id = force_str(urlsafe_base64_decode(id_base64))
            insurer = Insurer.objects.get(id=insurer_id)

            if not PasswordResetTokenGenerator().check_token(insurer, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            if new_password != confirm_password:
                raise ValidationError("Password Mismatch")

            if insurer.check_password(raw_password=new_password):
                raise ValidationError('Password must not be the same as the last')

            insurer.set_password(new_password)
            insurer.save()

        except Exception as e:
            raise e
        return attrs


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = [
            'id',
            'first_name',
            'last_name',
            'email'
        ]


class AgentsSignUpListSerializer(serializers.Serializer):
    names = serializers.CharField()
    emails = serializers.EmailField()


class CustomAgentSerializer(serializers.Serializer):
    agents_list = AgentsSignUpListSerializer(many=True)


class ViewInsurerDetails(serializers.ModelSerializer):
    class Meta:
        model = Insurer
        fields = [
            'id',
            'business_name',
            'email',
        ]


class InsurerClaimSellPolicySerializer(serializers.ModelSerializer):
    policy_name = serializers.CharField(max_length=100,
                                        min_length=1,
                                        allow_blank=False)

    class Meta:
        model = Insurer
        fields = [
            'policy_name'
        ]

    def validate(self, attrs):
        policy_name = attrs.get('policy_name')
        if not Policies.objects.filter(name=policy_name).exists():
            raise CustomValidationError({
                "error": f"Policy: {policy_name} does not exist"
            })

        return attrs


class CreatePolicies(serializers.ModelSerializer):
    name = serializers.CharField(max_length=200,
                                 allow_blank=False,
                                 allow_null=False,
                                 help_text="The name of the policy")
    policy_type = serializers.CharField(max_length=200,
                                        allow_blank=False,
                                        allow_null=False,
                                        help_text="The class a policy falls under. For now, we only support Device "
                                                  "Policies")
    amount = serializers.CharField(max_length=200,
                                   allow_blank=False,
                                   allow_null=False,
                                   help_text="Amount policy should be sold at")
    valid_from = serializers.DateTimeField(allow_null=False,
                                           help_text="Date at which policy is valid from")
    valid_to = serializers.DateTimeField(allow_null=False,
                                         help_text="Policy Expiration date")

    class Meta:
        model = Policies
        fields = [
            "name",
            "policy_type",
            "amount",
            "valid_from",
            "valid_to"
        ]

    def validate(self, attrs):
        valid_from, valid_to = attrs.get('valid_from'), attrs.get('valid_to')
        if valid_to < valid_from:
            raise ValidationError({"error": "valid_to must be greater than valid_from"}, 400)
        return attrs


class InsurerViewAllPolicies(serializers.ModelSerializer):
    class Meta:
        model = Policies
        fields = [
            'id',
            'name',
            'amount',
        ]


class InsurerProfileSerializier(serializers.Serializer):
    business_name = serializers.CharField()
    email = serializers.EmailField()
    profile_image = serializers.CharField()

    class Meta:
        fields = [
            'business_name',
            'profile_image',
            'email'
        ]


class UpdateProfileImageSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField()

    class Meta:
        model = InsurerProfile
        fields = [
            'profile_image'
        ]

    def update(self, instance, validated_data):
        instance.profile_image = validated_data.get('profile_image', instance.profile_image)
        instance.save()
        return instance
