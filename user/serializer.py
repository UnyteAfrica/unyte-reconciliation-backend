from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from agents.models import Agent

from .models import CustomUser


class SignInSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(allow_blank=False, allow_null=False, help_text='User password')

    class Meta:
        model = CustomUser
        fields = ['email', 'password']


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()

    class Meta:
        fields = ['email', 'otp']

    def validate(self, attrs):
        email = attrs.get('email')
        if not CustomUser.objects.filter(email=email).exists():
            raise ObjectDoesNotExist
        return attrs


class ForgotPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        user_email = attrs.get('email')
        if not CustomUser.objects.filter(email=user_email).exists():
            message = {'error': 'This email does not exist'}
            raise ValidationError(message)
        return attrs


class ForgotPasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=16)
    token = serializers.CharField(min_length=1)
    id_base64 = serializers.CharField(min_length=1)
    confirm_password = serializers.CharField(max_length=16)

    class Meta:
        fields = ['new_password', 'confirm_password', 'token', 'id_base64']

    def validate(self, attrs):
        try :
            token = attrs.get('token')
            id_base64 = attrs.get('id_base64')
            new_password = attrs.get('new_password')
            confirm_password = attrs.get('confirm_password')

            user_id = force_str(urlsafe_base64_decode(id_base64))
            user = CustomUser.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            if new_password != confirm_password:
                raise ValidationError('Password Mismatch')

            if user.check_password(raw_password=new_password):
                raise ValidationError('Password must not be the same as the last')

            user.set_password(new_password)
            user.save()

        except Exception as e:
            raise e
        return attrs


class SendNewOTPSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = CustomUser
        fields = ['email']


class ValidateRefreshToken(serializers.Serializer):
    refresh_token = serializers.CharField()


class ViewInsurerDetailsSerializer(serializers.Serializer):
    class Meta:
        fields = [
            'id',
            'business_name',
            'email',
        ]


class ViewAgentDetailsSerializer(serializers.Serializer):
    class Meta:
        fields = [
            'id',
            'first_name',
            'last_name',
            'middle_name',
            'email',
        ]


class ViewAgentProfileSerializer(serializers.Serializer):
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


class ViewInsurerProfileSerializer(serializers.Serializer):
    business_name = serializers.CharField()
    email = serializers.EmailField()
    profile_image = serializers.CharField()

    class Meta:
        fields = [
            'email' 'business_name',
            'profile_image',
        ]


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ['id', 'first_name', 'last_name', 'email']


class AgentsSignUpListSerializer(serializers.Serializer):
    names = serializers.CharField()
    emails = serializers.EmailField()


class CustomAgentSerializer(serializers.Serializer):
    agents_list = AgentsSignUpListSerializer(many=True)

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from agents.models import Agent

from .models import CustomUser


class SignInSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(allow_blank=False, allow_null=False, help_text='User password')

    class Meta:
        model = CustomUser
        fields = ['email', 'password']


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()

    class Meta:
        fields = ['email', 'otp']

    def validate(self, attrs):
        email = attrs.get('email')
        if not CustomUser.objects.filter(email=email).exists():
            raise ObjectDoesNotExist
        return attrs


class ForgotPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        user_email = attrs.get('email')
        if not CustomUser.objects.filter(email=user_email).exists():
            message = {'error': 'This email does not exist'}
            raise ValidationError(message)
        return attrs


class ForgotPasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=16)
    token = serializers.CharField(min_length=1)
    id_base64 = serializers.CharField(min_length=1)
    confirm_password = serializers.CharField(max_length=16)

    class Meta:
        fields = ['new_password', 'confirm_password', 'token', 'id_base64']

    def validate(self, attrs):
        try:
            token = attrs.get('token')
            id_base64 = attrs.get('id_base64')
            new_password = attrs.get('new_password')
            confirm_password = attrs.get('confirm_password')

            user_id = force_str(urlsafe_base64_decode(id_base64))
            user = CustomUser.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            if new_password != confirm_password:
                raise ValidationError('Password Mismatch')

            if user.check_password(raw_password=new_password):
                raise ValidationError('Password must not be the same as the last')

            user.set_password(new_password)
            user.save()

        except Exception as e:
            raise e
        return attrs


class SendNewOTPSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = CustomUser
        fields = ['email']


class ValidateRefreshToken(serializers.Serializer):
    refresh_token = serializers.CharField()


class ViewInsurerDetailsSerializer(serializers.Serializer):
    class Meta:
        fields = [
            'id',
            'business_name',
            'email',
        ]


class ViewAgentDetailsSerializer(serializers.Serializer):
    class Meta:
        fields = [
            'id',
            'first_name',
            'last_name',
            'middle_name',
            'email',
        ]


class ViewAgentProfileSerializer(serializers.Serializer):
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


class ViewInsurerProfileSerializer(serializers.Serializer):
    business_name = serializers.CharField()
    email = serializers.EmailField()
    profile_image = serializers.CharField()

    class Meta:
        fields = [
            'email' 'business_name',
            'profile_image',
        ]


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ['id', 'first_name', 'last_name', 'email']


class AgentsSignUpListSerializer(serializers.Serializer):
    names = serializers.CharField()
    emails = serializers.EmailField()


class CustomAgentSerializer(serializers.Serializer):
    agents_list = AgentsSignUpListSerializer(many=True)
