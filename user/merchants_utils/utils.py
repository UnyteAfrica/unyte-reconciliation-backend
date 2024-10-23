import csv
from io import TextIOWrapper

from rest_framework_simplejwt.tokens import RefreshToken

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import smart_bytes
from django.template.loader import render_to_string
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from insurer.utils import gen_absolute_url, verify_otp, generate_otp

from user.models import CustomUser
from user.serializer import CustomAgentSerializer, ViewMerchantDetailsSerializer, ViewInsurerProfileSerializer

from merchants.models import Merchant


def merchant_sign_in_insurer(user: CustomUser, insurer_email: str) -> Response:
    try:
        merchant: Merchant = Merchant.objects.get(user=user)

        otp = generate_otp()
        merchant.otp = otp
        merchant.otp_created_at = timezone.now().time()

        merchant.save()

        # TODO: Implement sending merchant sign in email
        # current_year = timezone.now().year
        # company_name = merchant.business_name
        # context = {'current_year': current_year, 'company_name': company_name, 'otp': otp}

        # html_message = render_to_string('otp.html', context)

        # send_mail(
        #     subject='Login OTP',
        #     message=f'{otp}',
        #     from_email=settings.EMAIL_HOST_USER,
        #     recipient_list=[settings.TO_EMAIL, insurer_email],
        #     html_message=html_message,
        # )
        message = {'message': 'OTP has been sent out to your email (No email)'}
        return Response(message, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status.HTTP_400_BAD_REQUEST)


def merchant_verify_otp_token(user: CustomUser, otp: str) -> Response:
    try:
        merchant = Merchant.objects.get(user=user)
        merchant_otp = merchant.otp

        if merchant_otp != otp:
            message = {'error': 'Incorrect OTP'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        otp_created_time = merchant_otp.otp_created_at
        verify = verify_otp(otp_created_time)

        if not verify:
            message = {'error': 'OTP has expired'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        auth_token = RefreshToken.for_user(user)

        message = {
            'login_status': True,
            'USER_TYPE': 'MERCHANT',
            'MERCHANT_ID': merchant.id,
            'access_token': str(auth_token.access_token),
            'refresh_token': str(auth_token),
        }

        return Response(message, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status.HTTP_400_BAD_REQUEST)


def merchant_forget_email_password(user: CustomUser, merchant_email: str) -> Response:
    merchant = Merchant.objects.get(user=user)

    if not user.is_insurer:
        return Response({'error': 'This user is not an merchant'}, status.HTTP_400_BAD_REQUEST)


    # TODO: Start looking at bugs at this point
    id_base64 = urlsafe_base64_encode(smart_bytes(user.id))
    token = PasswordResetTokenGenerator().make_token(user)

    """
    TODO: Edit email template
    """
    # abs_url = gen_absolute_url(id_base64, token)
    # current_year = timezone.now().year
    # company_name = insurer.business_name

    # context = {'id': id_base64, 'token': token, 'current_year': current_year, 'company_name': company_name}

    # html_message = render_to_string('forgot-password.html', context=context)

    # send_mail(
    #     subject='Forgot Password',
    #     message=f'{abs_url}',
    #     from_email=settings.EMAIL_HOST_USER,
    #     recipient_list=[settings.TO_EMAIL, merchant_email],
    #     html_message=html_message,
    # )


    message = {'message': f'Confirmation email sent, {id_base64} {token}'}
    return Response(message, status=status.HTTP_200_OK)


def merchant_reset_password(user: CustomUser, merchant_email: str) -> Response:
    try:
        if not user.is_insurer:
            return Response({'error': 'This user is not an merchant'}, status.HTTP_400_BAD_REQUEST)

        merchant = get_object_or_404(Merchant, user=user)

        otp = generate_otp()
        merchant.otp = otp
        merchant.otp_created_at = timezone.now().time()

        merchant.save()

        """
        TODO: Edit email template variables
        """
        # current_year = timezone.now().year
        # company_name = merchant.business_name
        # context = {'current_year': current_year, 'company_name': company_name, 'otp': otp}

        # html_message = render_to_string('otp.html', context)

        # send_mail(
        #     subject='Request New OTP',
        #     message=f'{otp}',
        #     from_email=settings.EMAIL_HOST_USER,
        #     recipient_list=[settings.TO_EMAIL, insurer_email],
        #     html_message=html_message,
        # )

        return Response({'message': f'New OTP sent out! {otp}'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status.HTTP_400_BAD_REQUEST)


def merchant_view_details(user: CustomUser) -> Response:
    merchant = get_object_or_404(Merchant, user=user)

    data = {'id': merchant.id, 'email': user.email, 'name': merchant.name}
    serializer_class = ViewMerchantDetailsSerializer(data=data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)

    return Response(serializer_class.data, status.HTTP_200_OK)


def merchant_view_profile(user: CustomUser) -> Response:
    """
    TODO:
     - Create MerchantProfile signal.
     - Create MerchantProfileSerializer.
    """
    # merchant = get_object_or_404(Merchant, user=user)
    # insurer_profile = get_object_or_404(InsurerProfile, insurer=insurer)

    # data = {
    #     'email': user.email,
    #     'business_name': insurer.business_name,
    #     'profile_image': insurer_profile.profile_image.url,
    # }

    # serializer_class = ViewInsurerProfileSerializer(data=data)
    # if not serializer_class.is_valid():
    #     return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)

    return Response({}, status.HTTP_200_OK)