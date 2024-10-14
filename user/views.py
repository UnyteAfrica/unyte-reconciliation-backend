from audioop import reverse
from datetime import datetime

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import DjangoUnicodeDecodeError, smart_str
from django.utils.http import urlsafe_base64_decode
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from agents.models import Agent
from insurer.models import Insurer
from insurer.utils import gen_sign_up_url_for_agent
from .agent_utils.utils import agent_sign_in, agent_verify_otp_token, agent_forget_email_password, agent_reset_password, \
    agent_view_details, agent_view_profile
from .insurer_utils.utils import insurer_sign_in_insurer, insurer_verify_otp_token, insurer_forget_email_password, \
    insurer_reset_password, insurer_view_details, insurer_view_profile, insurer_invite_agents, insurer_invite_agents_csv
from .models import CustomUser
from .serializer import SignInSerializer, VerifyOTPSerializer, ForgotPasswordEmailSerializer, \
    ForgotPasswordResetSerializer, SendNewOTPSerializer, ValidateRefreshToken, AgentSerializer, CustomAgentSerializer
from django.contrib.auth import authenticate
from drf_yasg.utils import swagger_auto_schema

SWAGGER_APP_TAG = 'User'


@swagger_auto_schema(
    method='POST',
    request_body=SignInSerializer,
    operation_description="User Login",
    responses={
        201: openapi.Response(
            'Created'
        ),
        400: 'Bad Request'
    },
    tags=[SWAGGER_APP_TAG]
)
@api_view(['POST'])
def sign_in(request: Request) -> Response:
    serializer_class = SignInSerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)

    email = serializer_class.validated_data.get("email")
    password = serializer_class.validated_data.get("password")

    try:
        user = authenticate(email=email, password=password)
        if not user:
            return Response({
                "error": "Failed to authenticate user"
            }, status.HTTP_400_BAD_REQUEST)

        user_obj = get_object_or_404(CustomUser, email=email)
        agent, insurer, merchant = user_obj.is_agent, user_obj.is_insurer, user_obj.is_merchant
        ROLE = ""
        if insurer:
            ROLE += "INSURER"
            return insurer_sign_in_insurer(user=user, insurer_email=email)

        if agent:
            ROLE += "AGENT"
            return agent_sign_in(user=user, agent_email=email)

        if merchant:
            ROLE += "MERCHANT"
            # TODO: Update this logic when Isaac implements merchant features
            USER_ROLE_ID = get_object_or_404(Agent, user=user_obj).id

    except Exception as e:
        return Response({
            "error": str(e)
        }, status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    request_body=VerifyOTPSerializer,
    operation_description="User Login",
    responses={
        201: openapi.Response(
            'Created'
        ),
        400: 'Bad Request'
    },
    tags=[SWAGGER_APP_TAG]
)
@api_view(['POST'])
def verify_otp(request: Request) -> Response:
    serializer_class = VerifyOTPSerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)

    email = serializer_class.validated_data.get("email")
    otp = serializer_class.validated_data.get("otp")

    user = get_object_or_404(CustomUser, email=email)

    try:
        agent, insurer, merchant = user.is_agent, user.is_insurer, user.is_merchant

        if insurer:
            return insurer_verify_otp_token(user, otp)

        if agent:
            return agent_verify_otp_token(user, otp)

        if merchant:
            pass

    except Exception as e:
        return Response({
            "error": str(e)
        }, status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    request_body=ForgotPasswordEmailSerializer,
    operation_description="User Login",
    responses={
        201: openapi.Response(
            'Created'
        ),
        400: 'Bad Request'
    },
    tags=[SWAGGER_APP_TAG]
)
@api_view(['POST'])
def forgot_email_password(request: Request) -> Response:
    serializer_class = ForgotPasswordEmailSerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)

    email = serializer_class.validated_data.get('email')
    user = get_object_or_404(CustomUser, email=email)

    try:
        agent, insurer, merchant = user.is_agent, user.is_insurer, user.is_merchant

        if agent:
            return agent_forget_email_password(user, email)

        if insurer:
            return insurer_forget_email_password(user, email)

        if merchant:
            pass

    except Exception as e:
        return Response({
            "error": str(e)
        }, status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='GET',
    operation_description='ID and Token Verification',
    responses={
        200: openapi.Response(
            'OK',
            # SuccessfulPasswordTokenCheckSerializer,
        ),
        400: 'Bad Request'
    },
    tags=[SWAGGER_APP_TAG]
)
@api_view(['GET'])
def password_token_check(request: Request, id_base64, token) -> Response:
    try:
        user_id = smart_str(urlsafe_base64_decode(id_base64))
        user = CustomUser.objects.get(id=user_id)

        if not PasswordResetTokenGenerator().check_token(user, token):
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
    operation_description='Resets Insurer forgotten password',
    request_body=ForgotPasswordResetSerializer,
    responses={
        200: openapi.Response(
            'OK',
            # SuccessfulResetPasswordSerializer,
        ),
        400: 'Bad Request'
    },
    tags=[SWAGGER_APP_TAG]
)
@api_view(['POST'])
def reset_password(request) -> Response:
    serializer_class = ForgotPasswordResetSerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "message": "Password successfully updated"
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='POST',
    request_body=SendNewOTPSerializer,
    operation_description='Sends new OTP to Insurer email',
    responses={
        200: openapi.Response(
            'OK',
            # SuccessfulSendNewOTPSerializer
        ),
        400: 'Bad Request'
    },
    tags=[SWAGGER_APP_TAG]
)
@api_view(['POST'])
def request_new_otp(request):
    serializer_class = SendNewOTPSerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer_class.validated_data.get('email')

    try:
        if not CustomUser.objects.filter(email=email).exists():
            return Response({
                "message": f"Email: {email} does not exists"
            }, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(CustomUser, email=email)
        agent, insurer, merchant = user.is_agent, user.is_insurer, user.is_merchant

        if agent:
            return agent_reset_password(user, email)

        if insurer:
            return insurer_reset_password(user, email)

        if merchant:
            pass

    except Exception as e:
        return Response({
            "error": str(e)
        }, status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    request_body=ValidateRefreshToken,
    operation_description='Sends new OTP to Insurer email',
    responses={
        200: openapi.Response(
            'OK',
            # SuccessfulSendNewOTPSerializer
        ),
        400: 'Bad Request'
    },
    tags=[SWAGGER_APP_TAG]
)
@api_view(['POST'])
def refresh_access_token(request):
    serializer_class = ValidateRefreshToken(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)

    try:
        refresh_token = serializer_class.validated_data.get('refresh_token')
        auth_token = RefreshToken(refresh_token)

        message = {
            "access": f"{auth_token.access_token}"
        }
        return Response(message, status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": f"The error '{e}' occurred"}, status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='GET',
    operation_description='User details',
    responses={
        200: openapi.Response(
            'OK',
            # SuccessfulSendNewOTPSerializer
        ),
        400: 'Bad Request'
    },
    tags=[SWAGGER_APP_TAG]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_details(request: Request) -> Response:
    user_id = request.user.id
    user = get_object_or_404(CustomUser, pk=user_id)

    try:
        agent, insurer, merchant = user.is_agent, user.is_insurer, user.is_merchant

        if agent:
            return agent_view_details(user)

        if insurer:
            return insurer_view_details(user)

        if merchant:
            pass

    except Exception as e:
        return Response({
            "error": str(e)
        }, status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='GET',
    operation_description='User profile',
    responses={
        200: openapi.Response(
            'OK',
            # SuccessfulSendNewOTPSerializer
        ),
        400: 'Bad Request'
    },
    tags=[SWAGGER_APP_TAG]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request: Request) -> Response:
    user_id = request.user.id
    user = get_object_or_404(CustomUser, pk=user_id)

    try:
        agent, insurer, merchant = user.is_agent, user.is_insurer, user.is_merchant

        if agent:
            return agent_view_profile(user)

        if insurer:
            return insurer_view_profile(user)

        if merchant:
            pass

    except Exception as e:
        return Response({
            "error": str(e)
        }, status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='GET',
    operation_description='View all agents invited by an Insurer',
    responses={
        200: openapi.Response(
            'OK',
            # SuccessfulListAllAgentsSerializer(many=True),
        ),
        403: 'Unauthorized',
        404: 'Not Found',
        400: 'Bad Request'
    },
    tags=[SWAGGER_APP_TAG]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_all_agents_for_insurer(request):
    user_id = request.user.id
    user = get_object_or_404(CustomUser, pk=user_id)

    if not user.is_insurer:
        return Response({
            "error": "This user is not an insurer"
        }, status.HTTP_400_BAD_REQUEST)

    insurer = get_object_or_404(Insurer, user=user)
    query_set = insurer.agent_set.all()

    serializer_class = AgentSerializer(query_set, many=True)
    return Response(serializer_class.data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='POST',
    operation_description='Generate SignUp Link for Agents',
    request_body=CustomAgentSerializer,
    responses={
        200: openapi.Response(
            'OK',
            # SuccessfulInsurerAgentSignupSerializer,
        ),
        400: 'Bad Request',
        404: 'Not Found'
    },
    tags=[SWAGGER_APP_TAG]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def invite_agents(request):

    user_id = request.user.id
    user = get_object_or_404(CustomUser, pk=user_id)

    if not user.is_insurer:
        return Response({
            "error": "This user is not an insurer"
        }, status.HTTP_400_BAD_REQUEST)

    try:
        return insurer_invite_agents(user, data=request.data)

    except Exception as e:
        return Response({
            "error": str(e)
        }, status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    operation_description='Generate SignUp Link for Agents through CSV file',
    responses={
        200: openapi.Response(
            'OK',
            # SuccessfulInsurerAgentSignupCSVSerializer,
        ),
        400: 'Bad Request',
        404: 'Not Found'
    },
    tags=[SWAGGER_APP_TAG]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def invite_agents_csv(request):
    user = get_object_or_404(CustomUser, pk=request.user.id)
    if not user.is_insurer:
        return Response({
            "error": "This user is not an insurer"
        }, status.HTTP_400_BAD_REQUEST)

    try:
        return insurer_invite_agents_csv(user, request=request)

    except Exception as e:
        return Response({
            "error": str(e)
        }, status.HTTP_400_BAD_REQUEST)