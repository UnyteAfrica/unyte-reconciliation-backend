import csv
from io import TextIOWrapper

from django.urls import reverse
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
from rest_framework.request import Request
from rest_framework.response import Response

from insurer.utils import verify_otp, generate_otp, gen_absolute_url, gen_sign_up_url_for_agent
from insurer.models import Insurer, InsurerProfile
from insurer.serializer import UploadCSVFileSerializer

from user.models import CustomUser
from user.serializer import CustomAgentSerializer, ViewInsurerDetailsSerializer, ViewInsurerProfileSerializer


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
    serializer_class = ViewInsurerDetailsSerializer(data=data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)

    return Response(serializer_class.data, status.HTTP_200_OK)


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


def insurer_invite_agents(user: CustomUser, data) -> Response:
    serializer_class = CustomAgentSerializer(data=data)
    insurer = get_object_or_404(Insurer, user=user)
    unyte_unique_insurer_id = insurer.unyte_unique_insurer_id

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)

    agent_list = serializer_class.validated_data.get('agents_list')
    email_recipients = []

    relative_link = '/user/agents/api'
    link = gen_sign_up_url_for_agent(relative_link, unyte_unique_insurer_id)

    current_year = timezone.now().year
    company_name = insurer.business_name

    for agent in agent_list:
        name = agent['names']
        email = agent['emails']

        context = {
            'current_year': current_year,
            'company_name': company_name,
            'unyte_unique_insurer_id': unyte_unique_insurer_id,
            'name': name,
        }
        html_message = render_to_string('invitation.html', context)
        email_recipients.append(email)
        """
        Sends email to the email of agents
        """
        send_mail(
            subject='Agent SignUp Link',
            message=f'{link}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=email_recipients,
            html_message=html_message,
        )
        email_recipients.pop(0)

    return Response({'message': f'Link generated: {link}'})


def insurer_invite_agents_csv(user: CustomUser, request: Request) -> Response:
    serializer_class = UploadCSVFileSerializer(data=request.data)
    insurer = get_object_or_404(Insurer, user=user)
    unyte_unique_insurer_id = insurer.unyte_unique_insurer_id
    company_name = insurer.business_name
    current_year = timezone.now().year

    relative_link = reverse('agents:register_agent')
    link = gen_sign_up_url_for_agent(relative_link, unyte_unique_insurer_id)

    try:
        otp = serializer_class.validated_data.get('otp')

        if otp != insurer.otp:
            return Response({'error': 'Invalid OTP'}, status.HTTP_400_BAD_REQUEST)

        otp_created_time = insurer.otp_created_at
        verify = verify_otp(otp_created_time)

        if not verify:
            message = {'error': 'OTP has expired'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['agents_csv']
        file_extension = file.name.split('.')[-1]
        if file_extension != 'csv':
            return Response(
                {'error': f'Unacceptable file format {file_extension}. Must be a csv file'},
                status.HTTP_400_BAD_REQUEST,
            )
        csv_file = TextIOWrapper(file.file, encoding='utf-8')
        csv_reader = csv.reader(csv_file, delimiter=',')
        all_rows = list(csv_reader)
        for agent in range(len(all_rows)):
            if agent == 0:
                pass
            else:
                agent_name = all_rows[agent][0]
                agent_email = all_rows[agent][1]

                context = {
                    'current_year': current_year,
                    'company_name': company_name,
                    'unyte_unique_insurer_id': unyte_unique_insurer_id,
                    'name': agent_name,
                }
                html_message = render_to_string('invitation.html', context)
                """
                Sends email to the email of agents
                """
                send_mail(
                    subject='Agent SignUp Link',
                    message=f'{link}',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[agent_email, settings.TO_EMAIL],
                    html_message=html_message,
                )
        return Response({'message': f'Successfully sent out invite links to {len(all_rows) - 1} agent(s)'})
    except Exception as e:
        return Response({'error': f'{e.__str__()}'}, status.HTTP_400_BAD_REQUEST)
