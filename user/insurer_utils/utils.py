from rest_framework_simplejwt.tokens import RefreshToken

from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import smart_bytes
from django.template.loader import render_to_string
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from rest_framework import status
from rest_framework.response import Response

from insurer.utils import verify_otp, generate_otp, gen_absolute_url
from insurer.models import Insurer, InsurerProfile

from user.models import CustomUser
from user.serializer import ViewInsurerProfileSerializer


def insurer_sign_in_insurer(user: CustomUser, insurer_email: str) -> Response:
    try:
        insurer: Insurer = Insurer.objects.get(user=user)

        otp = generate_otp()
        insurer.otp = otp
        insurer.otp_created_at = timezone.now().time()

        insurer.save()

        current_year = timezone.now().year
        company_name = insurer.business_name
        context = {'current_year': current_year, 'company_name': company_name, 'otp': otp}

        html_message = render_to_string('otp.html', context)

        send_mail(
            subject='Login OTP',
            message=f'{otp}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.TO_EMAIL, insurer_email],
            html_message=html_message,
        )
        message = {'message': 'OTP has been sent out to your email'}
        return Response(message, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status.HTTP_400_BAD_REQUEST)


def insurer_verify_otp_token(user: CustomUser, otp: str) -> Response:
    try:
        insurer = Insurer.objects.get(user=user)
        insurer_otp = insurer.otp

        if insurer_otp != otp:
            message = {'error': 'Incorrect OTP'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        otp_created_time = insurer.otp_created_at
        verify = verify_otp(otp_created_time)

        if not verify:
            message = {'error': 'OTP has expired'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        auth_token = RefreshToken.for_user(user)

        message = {
            'login_status': True,
            'USER_TYPE': 'INSURER',
            'INSURER_ID': insurer.id,
            'access_token': str(auth_token.access_token),
            'refresh_token': str(auth_token),
        }

        return Response(message, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status.HTTP_400_BAD_REQUEST)


def insurer_forget_email_password(user: CustomUser, insurer_email: str) -> Response:
    insurer = Insurer.objects.get(user=user)

    if not user.is_insurer:
        return Response({'error': 'This user is not an insurer'}, status.HTTP_400_BAD_REQUEST)

    id_base64 = urlsafe_base64_encode(smart_bytes(user.id))
    token = PasswordResetTokenGenerator().make_token(user)
    abs_url = gen_absolute_url(id_base64, token)
    current_year = timezone.now().year
    company_name = insurer.business_name

    context = {'id': id_base64, 'token': token, 'current_year': current_year, 'company_name': company_name}

    html_message = render_to_string('forgot-password.html', context=context)

    send_mail(
        subject='Forgot Password',
        message=f'{abs_url}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.TO_EMAIL, insurer_email],
        html_message=html_message,
    )

    message = {'message': 'Confirmation email sent'}
    return Response(message, status=status.HTTP_200_OK)


def insurer_reset_password(user: CustomUser, insurer_email: str) -> Response:
    try:
        if not user.is_insurer:
            return Response({'error': 'This user is not an insurer'}, status.HTTP_400_BAD_REQUEST)

        insurer = get_object_or_404(Insurer, user=user)

        otp = generate_otp()
        insurer.otp = otp
        insurer.otp_created_at = timezone.now().time()

        insurer.save()

        current_year = timezone.now().year
        company_name = insurer.business_name
        context = {'current_year': current_year, 'company_name': company_name, 'otp': otp}

        html_message = render_to_string('otp.html', context)

        send_mail(
            subject='Request New OTP',
            message=f'{otp}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.TO_EMAIL, insurer_email],
            html_message=html_message,
        )

        return Response({'message': 'New OTP sent out!'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status.HTTP_400_BAD_REQUEST)


def insurer_view_details(user: CustomUser) -> Response:
    insurer = get_object_or_404(Insurer, user=user)

    data = {'id': insurer.id, 'email': user.email, 'business_name': insurer.business_name}

    return Response(data, status.HTTP_200_OK)


def insurer_view_profile(user: CustomUser) -> Response:
    insurer = get_object_or_404(Insurer, user=user)
    insurer_profile = get_object_or_404(InsurerProfile, insurer=insurer)

    data = {
        'email': user.email,
        'business_name': insurer.business_name,
        'profile_image': insurer_profile.profile_image.url,
    }

    serializer_class = ViewInsurerProfileSerializer(data=data)
    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)

    return Response(serializer_class.data, status.HTTP_200_OK)
