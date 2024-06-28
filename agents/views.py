from django.contrib.auth import authenticate, login
from dotenv import load_dotenv, find_dotenv
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from .utils import send_otp, verify_otp
from .models import Agent
from rest_framework import status
from .serializer import CreateAgentSerializer, LoginAgentSerializer, AgentSendNewOTPSerializer, AgentOTPSerializer, \
    AgentForgotPasswordEmailSerializer, AgentForgotPasswordResetSerializer


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

        """
            Send email to insurer including otp.
        """
        send_otp(request, agent_email)
        serializer_class.save()
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

    send_otp(request, agent_email=agent_email)

    return Response({
        "message": "New OTP sent out!"
    }, status=status.HTTP_200_OK)


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
@permission_classes([AllowAny])
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
        print(serializer_class.validated_data)
        otp = serializer_class.validated_data.get('otp')
        if not verify_otp(request, otp):
            return Response({
                "message": "Invalid OTP, request for new OTP!"
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": "OTP Verified"
        }, status=status.HTTP_200_OK)

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

    insurer_email = serializer_class.validated_data.get('email')

    try:
        insurer = Agent.objects.get(email=insurer_email)
        auth_token = RefreshToken.for_user(insurer)
        message = {
            "access_token": str(auth_token.access_token),
            "refresh_token": str(auth_token)
        }
        return Response(message, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            f"The error '{e}' occurred"
        }, status=status.HTTP_400_BAD_REQUEST)


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
@permission_classes([IsAuthenticated])
def reset_password(request) -> Response:
    serializer_class = AgentForgotPasswordResetSerializer(data=request.data)
    user = request.user

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

    new_password = serializer_class.validated_data.get('new_password')

    try:
        insurer = Agent.objects.get(username=user)
        if insurer.check_password(raw_password=new_password):
            return Response({
                "message": "New password cannot be the same with old password"
            }, status=status.HTTP_400_BAD_REQUEST)

        insurer.set_password(new_password)
        insurer.save()

        return Response({
            "message": "Password successfully updated"
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            f"The error '{e}' occurred"
        }, status=status.HTTP_400_BAD_REQUEST)