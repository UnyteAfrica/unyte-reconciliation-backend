from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from rest_framework import serializers
from rest_framework.exceptions import ValidationError, AuthenticationFailed

from user.models import CustomUser

from .utils import CustomValidationError
from .models import Agent


class CreateAgentSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=30, required=True, allow_null=False, allow_blank=False)
    last_name = serializers.CharField(max_length=30, required=True, allow_null=False, allow_blank=False)
    middle_name = serializers.CharField(allow_blank=False, allow_null=False)
    home_address = serializers.CharField(max_length=255, allow_null=False, allow_blank=False)
    email = serializers.EmailField()
    bank_account = serializers.CharField(min_length=10, max_length=10, allow_blank=False, allow_null=False)
    bvn = serializers.CharField(min_length=11, max_length=11, allow_null=False, allow_blank=False)
    # agent_gamp_id = serializers.CharField(allow_null=True,
    #                                      allow_blank=True)
    password = serializers.CharField(max_length=16, allow_blank=False, allow_null=False)

    class Meta:
        fields = [
            "first_name",
            "last_name",
            "middle_name",
            "home_address",
            "email",
            "bank_account",
            "bvn",
            # "agent_gamp_id",
            "password",
        ]

    def validate(self, attrs):
        # agent_gamp_id = attrs.get('agent_gamp_id')
        # first_name = attrs.get('first_name')
        # middle_name = attrs.get('middle_name')
        bank_account = attrs.get("bank_account")
        email = attrs.get("email")
        home_address = attrs.get("home_address")
        bvn = attrs.get("bvn")

        # print(middle_name)

        # if agent_gamp_id == '' or middle_name == '':
        #     if Agent.objects.filter(email=email).exists():
        #         raise CustomValidationError({"error": "Email already exists"})

        if CustomUser.objects.filter(email=email).exists():
            raise CustomValidationError({"error": "Email already exists!"})

        if Agent.objects.filter(home_address=home_address).exists():
            raise CustomValidationError({"error": "Home address already exists"})

        if Agent.objects.filter(bvn=bvn).exists():
            raise CustomValidationError({"error": "bvn already exists"})

        if Agent.objects.filter(bank_account=bank_account).exists():
            raise CustomValidationError({"error": "bank_account already exists"})

        #     return attrs
        #
        # else:
        #     if Agent.objects.filter(email=email).exists():
        #         raise CustomValidationError({"error": "Email already exists"})
        #
        #     if custom_user.objects.filter(email=email).exists():
        #         raise CustomValidationError({"error": "Email already exists!"})
        #
        #     if Agent.objects.filter(home_address=home_address).exists():
        #         raise CustomValidationError({"error": "Home address already exists"})
        #
        #     if Agent.objects.filter(bvn=bvn).exists():
        #         raise CustomValidationError({"error": "bvn already exists"})
        #
        #     if Agent.objects.filter(bank_account=bank_account).exists():
        #         raise CustomValidationError({"error": "bank_account already exists"})
        #
        #     pattern = f'{first_name}+{bank_account}@getgamp.com'
        #
        #     if agent_gamp_id != pattern:
        #         raise CustomValidationError({"error": "Invalid GampID"})
        #
        #     if Agent.objects.filter(agent_gamp_id=agent_gamp_id).exists():
        #         raise CustomValidationError({"error": "GampID already exists"})

        return attrs


class AgentValidateRefreshToken(serializers.Serializer):
    refresh_token = serializers.CharField()


class LoginAgentSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        fields = ["email", "password"]


class LogoutAgentSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    class Meta:
        fields = ["refresh"]

    def save(self):
        refresh_token = self.validated_data.get("refresh")
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except (ObjectDoesNotExist, TokenError) as err:
            return CustomValidationError({"error": str(err)})


class AgentOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(required=False, max_length=6)


class AgentSendNewOTPSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = Agent
        fields = ["email"]


class AgentForgotPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ["email"]

    def validate(self, attrs):
        agent_email = attrs.get("email")
        if not CustomUser.objects.filter(email=agent_email, is_agent=True).exists():
            message = {"error": "This email does not exist"}
            raise ValidationError(message)
        return attrs


class AgentForgotPasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=16)
    token = serializers.CharField(min_length=1)
    id_base64 = serializers.CharField(min_length=1)
    confirm_password = serializers.CharField(max_length=16)

    class Meta:
        fields = ["new_password", "confirm_password", "token", "id_base64"]

    def validate(self, attrs):
        try:
            token = attrs.get("token")
            id_base64 = attrs.get("id_base64")
            new_password = attrs.get("new_password")
            confirm_password = attrs.get("confirm_password")

            user_id = force_str(urlsafe_base64_decode(id_base64))
            user = get_object_or_404(CustomUser, pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("The reset link is invalid", 401)

            if new_password != confirm_password:
                raise ValidationError("Password Mismatch")

            if user.check_password(raw_password=new_password):
                raise ValidationError("Password must not be the same as the last")

            user.set_password(new_password)
            user.save()

        except Exception as e:
            raise e
        return attrs


class ViewAgentDetailsSerializer(serializers.Serializer):
    class Meta:
        fields = [
            "id",
            "first_name",
            "last_name",
            "middle_name",
            "email",
        ]


class PolicyProductTypeSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, allow_blank=False, help_text="Name of policy product type")
    premium = serializers.CharField(max_length=100, allow_blank=False, help_text="Price of product type")
    flat_fee = serializers.CharField(max_length=3, allow_blank=False, help_text="Flat fee availability")


class AgentSellPolicySerializer(serializers.Serializer):
    policy_name = serializers.CharField(max_length=100, min_length=1, allow_blank=False)
    product_type = PolicyProductTypeSerializer(many=True)

    class Meta:
        fields = ["policy_name", "product_type"]


class ViewAgentProfile(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    middle_name = serializers.CharField()
    profile_image = serializers.CharField()

    class Meta:
        fields = [
            "email",
            "first_name",
            "last_name",
            "middle_name",
            "profile_image",
        ]
