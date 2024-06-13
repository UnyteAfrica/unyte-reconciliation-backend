from rest_framework import serializers
from .models import Insurer


class CreateInsurerSerializer(serializers.ModelSerializer):

    username = serializers.CharField(max_length=12)
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
    new_otp = serializers.CharField(required=False, max_length=6)
