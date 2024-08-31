from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from insurer.models import Insurer
from .models import Agent
from rest_framework import serializers
from datetime import datetime
from .utils import generate_otp, CustomValidationError
from policies.models import AgentPolicy, Policies

custom_user = get_user_model()


class CreateAgentSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=30,
                                       required=True,
                                       allow_null=False,
                                       allow_blank=False)
    last_name = serializers.CharField(max_length=30,
                                      required=True,
                                      allow_null=False,
                                      allow_blank=False)
    middle_name = serializers.CharField(allow_blank=False,
                                        allow_null=False)
    home_address = serializers.CharField(max_length=255,
                                         allow_null=False,
                                         allow_blank=False)
    email = serializers.EmailField()
    bank_account = serializers.CharField(min_length=10,
                                         max_length=10,
                                         allow_blank=False,
                                         allow_null=False)
    bvn = serializers.CharField(min_length=11,
                                max_length=11,
                                allow_null=False,
                                allow_blank=False)
    agent_gampID = serializers.CharField(allow_null=True,
                                         allow_blank=True)
    password = serializers.CharField(max_length=16,
                                     allow_blank=False,
                                     allow_null=False)

    class Meta:
        model = Agent
        fields = [
            "first_name",
            "last_name",
            "middle_name",
            "home_address",
            "email",
            "bank_account",
            "bvn",
            "agent_gampID",
            "password"
        ]

    def validate(self, attrs):
        agent_gampID = attrs.get('agent_gampID')
        first_name = attrs.get('first_name')
        middle_name = attrs.get('middle_name')
        bank_account = attrs.get('bank_account')
        email = attrs.get('email')
        home_address = attrs.get('home_address')
        bvn = attrs.get('bvn')

        print(middle_name)

        if agent_gampID == '' or middle_name == '':
            if Agent.objects.filter(email=email).exists():
                raise CustomValidationError({"error": "Email already exists"})

            if custom_user.objects.filter(email=email).exists():
                raise CustomValidationError({"error": "Email already exists!"})

            if Agent.objects.filter(home_address=home_address).exists():
                raise CustomValidationError({"error": "Home address already exists"})

            if Agent.objects.filter(bvn=bvn).exists():
                raise CustomValidationError({"error": "bvn already exists"})

            if Agent.objects.filter(bank_account=bank_account).exists():
                raise CustomValidationError({"error": "bank_account already exists"})

            return attrs

        else:
            if Agent.objects.filter(email=email).exists():
                raise CustomValidationError({"error": "Email already exists"})

            if custom_user.objects.filter(email=email).exists():
                raise CustomValidationError({"error": "Email already exists!"})

            if Agent.objects.filter(home_address=home_address).exists():
                raise CustomValidationError({"error": "Home address already exists"})

            if Agent.objects.filter(bvn=bvn).exists():
                raise CustomValidationError({"error": "bvn already exists"})

            if Agent.objects.filter(bank_account=bank_account).exists():
                raise CustomValidationError({"error": "bank_account already exists"})

            pattern = f'{first_name}+{bank_account}@getgamp.com'

            if agent_gampID != pattern:
                raise CustomValidationError({"error": "Invalid GampID"})

            if Agent.objects.filter(agent_gampID=agent_gampID).exists():
                raise CustomValidationError({"error": "GampID already exists"})

            return attrs


class AgentValidateRefreshToken(serializers.Serializer):
    refresh_token = serializers.CharField()


class LoginAgentSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        model = Agent
        fields = [
            'email',
            'password'
        ]


class LogoutAgentSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    class Meta:
        fields = [
            'refresh'
        ]

    def save(self):
        refresh_token = self.validated_data.get('refresh')
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except (ObjectDoesNotExist, TokenError) as err:
            return CustomValidationError({
                "error": str(err)
            })


class AgentOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(required=False, max_length=6)


class AgentSendNewOTPSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = Agent
        fields = [
            'email'
        ]


class AgentForgotPasswordEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = Insurer
        fields = [
            'email'
        ]

    def validate(self, attrs):
        agent_email = attrs.get('email')
        if not Agent.objects.filter(email=agent_email).exists():
            message = {
                "error": "This email does not exist"
            }
            raise ValidationError(message)
        return attrs


class AgentForgotPasswordResetSerializer(serializers.Serializer):
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

            agent_id = force_str(urlsafe_base64_decode(id_base64))
            agent = Agent.objects.get(id=agent_id)

            if not PasswordResetTokenGenerator().check_token(agent, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            if new_password != confirm_password:
                raise ValidationError("Password Mismatch")

            if agent.check_password(raw_password=new_password):
                raise ValidationError('Password must not be the same as the last')

            agent.set_password(new_password)
            agent.save()

        except Exception as e:
            raise e
        return attrs


class ViewAgentDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = [
            'id',
            'first_name',
            'last_name',
            'middle_name',
            'email',
        ]


class PolicyProductTypeSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100,
                                 allow_blank=False,
                                 help_text="Name of policy product type")
    premium = serializers.CharField(max_length=100,
                                    allow_blank=False,
                                    help_text="Price of product type")
    flat_fee = serializers.CharField(max_length=3,
                                     allow_blank=False,
                                     help_text="Flat fee availability")
    broker_commission = serializers.DecimalField(max_digits=5,
                                                 decimal_places=2,
                                                 help_text="Commission attached to a product")


class AgentSellPolicySerializer(serializers.ModelSerializer):
    policy_name = serializers.CharField(max_length=100,
                                        min_length=1,
                                        allow_blank=False)
    quantity_to_sell = serializers.IntegerField(allow_null=False,
                                                default=0)
    product_type = PolicyProductTypeSerializer(many=True)

    class Meta:
        model = Agent
        fields = [
            'policy_name',
            'quantity_to_sell',
            'product_type'
        ]


class AgentClaimPolicySerializer(serializers.ModelSerializer):
    policy_name = serializers.CharField(max_length=100,
                                        min_length=1,
                                        allow_blank=False)
    quantity_bought = serializers.IntegerField(allow_null=False,
                                               default=0)

    class Meta:
        model = Agent
        fields = [
            'policy_name',
            'quantity_bought'
        ]

    def validate(self, attrs):
        policy_name = attrs.get('policy_name')
        if not Policies.objects.filter(name=policy_name).exists():
            raise CustomValidationError({
                "error": f"Policy: {policy_name} does not exist"
            })

        return attrs


class AgentPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policies
        fields = [
            'name',
            'amount',
            'valid_from',
            'valid_to'
        ]


class AgentViewAllClaimedPolicies(serializers.ModelSerializer):
    policy = AgentPolicySerializer()

    class Meta:
        model = AgentPolicy
        fields = [
            'id',
            'policy',
            'quantity_bought',
            'quantity_sold'
        ]


class AgentViewAllAvailablePolicies(serializers.ModelSerializer):
    class Meta:
        model = Policies
        fields = [
            'id',
            'name',
            'policy_category',
            'valid_to',
            'valid_from'
        ]


class ViewAgentProfile(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    middle_name = serializers.CharField()
    profile_image = serializers.CharField()

    class Meta:
        fields = [
            'email',
            'first_name',
            'last_name',
            'middle_name',
            'profile_image',
        ]
