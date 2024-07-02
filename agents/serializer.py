import re

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework.exceptions import ValidationError, AuthenticationFailed

from insurer.models import Insurer
from .models import Agent
from rest_framework import serializers
from datetime import datetime
from .utils import generate_otp


class CreateAgentSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=30,
                                       allow_null=False,
                                       allow_blank=False)
    last_name = serializers.CharField(max_length=30,
                                      allow_null=False,
                                      allow_blank=False)
    middle_name = serializers.CharField(max_length=30,
                                        allow_blank=False,
                                        allow_null=False)
    home_address = serializers.CharField(max_length=255,
                                         allow_null=False,
                                         allow_blank=False)
    email = serializers.EmailField()
    bank_account = serializers.CharField(max_length=10,
                                         allow_blank=False,
                                         allow_null=False)
    bvn = serializers.CharField(max_length=11,
                                allow_null=False,
                                allow_blank=False)
    affiliated_company = serializers.CharField(allow_blank=False,
                                               allow_null=False)
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
            "affiliated_company",
            "agent_gampID",
            "password"
        ]

    def validate(self, attrs):
        agent_gampID = attrs.get('agent_gampID')
        first_name = attrs.get('first_name')
        bank_account = attrs.get('bank_account')

        if agent_gampID == '':
            return attrs

        pattern = f'{first_name}+{bank_account}@getgamp.com'

        print(pattern, agent_gampID)

        if agent_gampID != pattern:
            raise ValidationError("Invalid GampID")
        return attrs

    def create(self, validated_data):
        affiliated_company = validated_data.get('affiliated_company')

        insurer = Insurer.objects.filter(business_name=affiliated_company).exists()

        if not insurer:
            return "Affiliated company does not exist"

        insurer = Insurer.objects.get(business_name=affiliated_company)
        validated_data['affiliated_company'] = insurer

        agent = Agent.objects.create_user(**validated_data, otp=generate_otp(), otp_created_at=datetime.now().time())
        agent.save()
        return agent


class LoginAgentSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        model = Agent
        fields = [
            'email',
            'password'
        ]


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
