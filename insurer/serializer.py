from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.utils.encoding import force_str
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from rest_framework import serializers
from rest_framework.exceptions import ValidationError, AuthenticationFailed

from agents.models import Agent

from user.models import CustomUser

from .utils import CustomValidationError, generate_otp, generate_unyte_unique_insurer_id
from .models import Insurer, InsurerProfile

custom_user = get_user_model()


class CreateInsurerSerializer(serializers.Serializer):
    business_name = serializers.CharField(
        max_length=50, required=True, help_text='Insurer business name', allow_blank=False, allow_null=False
    )
    admin_name = serializers.CharField(
        max_length=20,
        required=True,
        help_text='Insurer account admin (handler) name',
        allow_blank=False,
        allow_null=False,
    )
    business_registration_number = serializers.CharField(
        max_length=8, min_length=8, required=True, help_text='Business registration number or Tax ID of insurer'
    )
    email = serializers.EmailField()
    password = serializers.CharField(max_length=16, allow_null=False, allow_blank=False)

    # insurer_gamp_id = serializers.CharField(allow_blank=True,
    #                                        allow_null=True)

    class Meta:
        fields = [
            'business_name',
            'admin_name',
            'business_registration_number',
            'email',
            'password',
            # 'insurer_gamp_id'
        ]

    def validate(self, attrs):
        attrs.get('insurer_gamp_id')
        attrs.get('admin_name')
        business_reg_num = attrs.get('business_registration_number')
        business_name = attrs.get('business_name')
        email = attrs.get('email')

        # if insurer_gamp_id == '':
        if custom_user.objects.filter(email=email).exists():
            raise CustomValidationError({'error': 'Email already exists'})

        if custom_user.objects.filter(email=email).exists():
            raise CustomValidationError({'error': 'Email already exists'})

        if Insurer.objects.filter(business_registration_number=business_reg_num).exists():
            raise CustomValidationError({'error': 'Business Registration number already exists'})

        if Insurer.objects.filter(business_name=business_name).exists():
            raise CustomValidationError({'error': 'Business Name  already exists'})

        # return attrs

        # else:
        #     if Insurer.objects.filter(insurer_gamp_id=insurer_gamp_id).exists():
        #         raise CustomValidationError({"error": "GampID already exists"})
        #
        #     if Insurer.objects.filter(email=email).exists():
        #         raise CustomValidationError({"error": "Email already exists"})
        #
        #     if custom_user.objects.filter(email=email).exists():
        #         raise CustomValidationError({"error": "Email already exists"})
        #
        #     if Insurer.objects.filter(business_registration_number=business_reg_num).exists():
        #         raise CustomValidationError({"error": "Business Registration number already exists"})
        #
        #     if Insurer.objects.filter(business_name=business_name).exists():
        #         raise CustomValidationError({"error": "Business Name  already exists"})
        #
        # pattern = f'{admin_name}+{business_reg_num}@getgamp.com'
        #
        # if insurer_gamp_id != pattern:
        #     raise CustomValidationError({"error": "Invalid GampID"})

        return attrs

    def create(self, validated_data):
        email = validated_data.get('email')
        password = validated_data.get('password')
        business_name = validated_data.get('business_name')
        business_reg_num = validated_data.get('business_registration_number')
        unyte_unique_insurer_id = generate_unyte_unique_insurer_id(business_name, business_reg_num)
        admin_name = validated_data.get('admin_name')

        user = CustomUser.objects.create_user(email=email, password=password, is_insurer=True)
        user.save()

        insurer = Insurer.objects.create(
            business_name=business_name,
            business_registration_number=business_reg_num,
            unyte_unique_insurer_id=unyte_unique_insurer_id,
            admin_name=admin_name,
            otp=generate_otp(),
            otp_created_at=timezone.now().time(),
            user=user,
        )
        insurer.save()
        return insurer


class LoginInsurerSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=255)

    class Meta:
        fields = ['email', 'password']


class ValidateRefreshToken(serializers.Serializer):
    refresh_token = serializers.CharField()


class OTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(required=False, max_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        if not CustomUser.objects.filter(email=email).exists():
            raise ObjectDoesNotExist
        return attrs


class VerifyInsurerSerializer(serializers.Serializer):
    otp = serializers.CharField(required=False, max_length=6)


class SendNewOTPSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = Insurer
        fields = ['email']


class InsurerForgotPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        insurer_email = attrs.get('email')
        if not CustomUser.objects.filter(email=insurer_email).exists():
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


class AgentSerializer(serializers.Serializer):
    class Meta:
        fields = ['id', 'first_name', 'last_name', 'email']


class AgentsSignUpListSerializer(serializers.Serializer):
    names = serializers.CharField()
    emails = serializers.EmailField()


class CustomAgentSerializer(serializers.Serializer):
    agents_list = AgentsSignUpListSerializer(many=True)


class ViewInsurerDetails(serializers.Serializer):
    class Meta:
        fields = [
            'id',
            'business_name',
            'email',
        ]


class InsurerProfileSerializer(serializers.Serializer):
    business_name = serializers.CharField()
    email = serializers.EmailField()
    profile_image = serializers.CharField()

    class Meta:
        fields = [
            'business_name',
            'profile_image',
        ]


class UpdateProfileImageSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField()

    class Meta:
        model = InsurerProfile
        fields = ['profile_image']

    def update(self, instance, validated_data):
        instance.profile_image = validated_data.get('profile_image', instance.profile_image)
        instance.save()
        return instance


class UploadCSVFileSerializer(serializers.Serializer):
    otp = serializers.CharField()
    agents_csv = serializers.FileField()

    class Meta:
        fields = ['otp', 'agents_csv']
