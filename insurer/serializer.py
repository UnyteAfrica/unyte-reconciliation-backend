from rest_framework import serializers
from .models import Insurer


class CreateInsurerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=15)
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=255)

    class Meta:
        model = Insurer
        fields = [
            'username',
            'email',
            'password',
        ]

    def validate(self, attrs):
        username = attrs.get('username', '')
        password = attrs.get('password', '')
        return super().validate(attrs)

    def create(self, validated_data):
        user = Insurer.objects.create_user(**validated_data)
        user.save()
        return user


class LoginInsurerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=12)
    password = serializers.CharField(max_length=255)

    class Meta:
        model = Insurer
        fields = [
            'username',
            'password'
        ]


class OTPSerializer(serializers.Serializer):
    otp = serializers.CharField(required=False, max_length=6)


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

    def check_passwords_equal(self) -> str:
        new_password = self.validated_data.get('new_password')
        confirm_password = self.validated_data.get('confirm_password')

        if new_password != confirm_password:
            return "Passwords don't match"
