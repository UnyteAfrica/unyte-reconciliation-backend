from django.conf import settings
from django.contrib.auth import authenticate
from datetime import datetime

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError, smart_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from .utils import generate_otp, verify_otp, gen_absolute_url
from .models import Agent
from rest_framework import status
from .serializer import CreateAgentSerializer, LoginAgentSerializer, AgentSendNewOTPSerializer, AgentOTPSerializer, \
    AgentForgotPasswordEmailSerializer, AgentForgotPasswordResetSerializer, ViewAgentDetailsSerializer, \
    UpdateAgentDetails


@swagger_auto_schema(
    method='POST',
    request_body=CreateAgentSerializer,
    operation_description='Create New Agent',
    responses={
        '201': "Created",
        '400': 'Bad Request'
    },
    tags=['Agent']
)
@api_view(['POST'])
def create_agent(request) -> Response:
    serializer_class = CreateAgentSerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        first_name = serializer_class.validated_data.get('first_name')
        last_name = serializer_class.validated_data.get('last_name')
        agent_email = serializer_class.validated_data.get('email')

        serializer_class.save()

        """
            Send email to insurer including otp.
        """
        agent = Agent.objects.get(email=agent_email)
        otp = agent.otp
        send_mail(
            subject='Verification email',
            message=f'{otp}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.TO_EMAIL, agent_email],
        )

        message = {
            'message': f'Account successfully created for {first_name} {last_name}'
        }
        return Response(message, status=status.HTTP_201_CREATED)

    except Exception as e:
        message = {
            "error": e.__str__()
        }
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    request_body=LoginAgentSerializer,
    operation_description='Login Agent',
    responses={
        '200': "OK",
        '400': 'Bad Request'
    },
    tags=['Agent']
)
@api_view(['POST'])
def login_agent(request) -> Response:
    serializer_class = LoginAgentSerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

    agent_email = serializer_class.validated_data.get('email')
    agent_password = serializer_class.validated_data.get('password')

    try:
        user = authenticate(email=agent_email, password=agent_password)
        if user is None:
            message = {
                "error": "Failed to authenticate agent"
            }
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        agent = Agent.objects.get(email=agent_email)
        auth_token = RefreshToken.for_user(agent)

        message = {
            "login_status": True,
            "access_token": str(auth_token.access_token),
            "refresh_token": str(auth_token)
        }

        return Response(message, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({f"The error {e.__str__()} occurred"}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    request_body=AgentSendNewOTPSerializer,
    operation_description='Request New OTP',
    responses={
        200: 'OK',
        400: 'Bad Request'
    },
    tags=['Agent']
)
@api_view(['POST'])
def request_new_otp(request):
    serializer_class = AgentSendNewOTPSerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

    agent_email = serializer_class.validated_data.get('email')

    if not Agent.objects.filter(email=agent_email).exists():
        return Response({
            "message": f"Email: {agent_email} does not exists"
        }, status=status.HTTP_400_BAD_REQUEST)

    agent = Agent.objects.get(email=agent_email)

    otp = generate_otp()
    agent.otp = otp
    agent.otp_created_at = datetime.now().time()

    agent.save()

    send_mail(
        subject='Verification email',
        message=f'{otp}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.TO_EMAIL, agent_email],
    )
    message = {
        'message': 'New OTP has been sent out!'
    }
    return Response(message, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='POST',
    request_body=AgentOTPSerializer,
    operation_description='Verify OTP',
    responses={
        200: 'OK',
        400: 'Bad Request'
    },
    tags=['Agent']
)
@api_view(['POST'])
def verify_otp_token(request) -> Response:
    """
    Verify OTP endpoint
    :param request:
    :return: Response
    """
    serializer_class = AgentOTPSerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        otp = serializer_class.validated_data.get('otp')
        agent_email = serializer_class.validated_data.get('email')

        agent = Agent.objects.get(email=agent_email)

        agent_otp = agent.otp

        if agent_otp != otp:
            message = {
                "error": "Incorrect OTP"
            }
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        otp_created_time = agent.otp_created_at
        verify = verify_otp(otp_created_time)

        if not verify:
            message = {
                'error': 'OTP has expired'
            }
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        message = {
            'error': 'OTP Verified'
        }
        return Response(message, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({f"The error {e.__str__()} occurred"}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    operation_description='Send Verification OTP to Insurer Email',
    request_body=AgentForgotPasswordEmailSerializer,
    responses={
        200: 'OK',
        400: 'Bad Request'
    },
    tags=['Agent']
)
@api_view(['POST'])
def forgot_password_email(request) -> Response:
    serializer_class = AgentForgotPasswordEmailSerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

    agent_email = serializer_class.validated_data.get('email')

    try:
        agent = Agent.objects.get(email=agent_email)
        id_base64 = urlsafe_base64_encode(smart_bytes(agent.id))
        token = PasswordResetTokenGenerator().make_token(agent)
        current_site = get_current_site(request).domain
        relative_link = reverse('agents:password-reset-confirm', kwargs={'id_base64': id_base64, 'token': token})
        abs_url = gen_absolute_url(current_site, relative_link, token)

        send_mail(
            subject='Verification email',
            message=f'{abs_url}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.TO_EMAIL, agent_email],
        )

        message = {
            "message": "Confirmation email sent"
        }
        return Response(message, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "error": f"{e}"
        }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='GET',
    operation_description='Id and Token Verification',
    responses={
        200: 'OK',
        400: 'Bad Request'
    },
    tags=['Agent']
)
@api_view(['GET'])
def password_token_check(request, id_base64, token):
    try:
        agent_id = smart_str(urlsafe_base64_decode(id_base64))
        agent = Agent.objects.get(id=agent_id)

        if not PasswordResetTokenGenerator().check_token(agent, token):
            return Response({
                "error": "Token is invalid, request a new one"
            }, status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": "Valid Token",
            "id_base64": id_base64,
            "token": token
        }, status=status.HTTP_200_OK)

    except DjangoUnicodeDecodeError as e:
        return Response({
            "error": f"{e.__str__()}"
        }, status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    operation_description='Reset Password',
    request_body=AgentForgotPasswordResetSerializer,
    responses={
        200: 'OK',
        400: 'Bad Request'
    },
    tags=['Agent']
)
@api_view(['POST'])
def reset_password(request) -> Response:
    serializer_class = AgentForgotPasswordResetSerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "message": "Password successfully updated"
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='GET',
    operation_description='View Agent Details',
    responses={
        200: 'OK',
        400: 'Bad Request',
        404: 'Not Found'
    },
    tags=['Agent']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_agent_details(request, pk):
    agent = get_object_or_404(Agent, pk=pk)
    serializer_class = ViewAgentDetailsSerializer(agent)

    return Response(serializer_class.data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='PATCH',
    operation_description='Update Agent Details',
    request_body=UpdateAgentDetails,
    responses={
        200: 'OK',
        400: 'Bad Request',
        404: 'Not Found'
    },
    tags=['Agent']
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_agent_details(request, pk):
    valid_pk = int(pk)
    if request.user.id != valid_pk:
        return Response({
            "error": "You are Unauthorized to complete this action"
        }, status.HTTP_401_UNAUTHORIZED)
    serializer_class = UpdateAgentDetails(request.user, data=request.data, partial=True)

    if not serializer_class.is_valid():
        return Response({
            "error": f"{serializer_class.errors}"
        }, status.HTTP_400_BAD_REQUEST)

    try:
        serializer_class.save()
        return Response({
            "message": "Agent data successfully updated"
        }, status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "error": f"{e}"
        }, status.HTTP_400_BAD_REQUEST)