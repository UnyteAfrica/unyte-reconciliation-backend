from django.contrib.auth import authenticate, login
from dotenv import load_dotenv, find_dotenv
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializer import CreateInsurerSerializer, LoginInsurerSerializer, OTPSerializer, ForgotPasswordEmailSerializer, \
    ForgotPasswordResetSerializer, VerifyInsurerSerializer
from rest_framework.response import Response
from .models import Insurer
from drf_yasg.utils import swagger_auto_schema
from .utils import send_otp, verify_otp

load_dotenv(find_dotenv())


def store_insurer_profile_pictures(profile_picture):
    """
    Store profile picture in GCP
    :param profile_picture: string
    :return: string
    """
    return


@swagger_auto_schema(
    method='POST',
    request_body=CreateInsurerSerializer,
    operation_description="Create new insurer",
    responses={
        201: 'Created',
        400: 'Bad Request'
    },
    tags=['Insurer']
)
@api_view(['POST'])
def create_insurer(request) -> Response:
    """
    Create insurer by using params from CreateInsurerSerializer
    :param request:
    :return: Response
    """
    serializer_class = CreateInsurerSerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        insurer_name = serializer_class.validated_data.get('username')
        insurer_email = serializer_class.validated_data.get('email')

        """
        Send email to insurer including otp.
        """
        send_otp(request, insurer_email)
        serializer_class.save()

        insurer = Insurer.objects.get(username=insurer_name)
        auth_token = RefreshToken.for_user(insurer)

        message = {
            "message": f"Account successfully created for user: {insurer_name}",
            "access_token": str(auth_token.access_token),
            "refresh_token": str(auth_token)
        }
        return Response(message, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({f"The error {e.__str__()} occurred"}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    request_body=LoginInsurerSerializer,
    operation_description='Login Insurer',
    responses={
        200: 'OK',
        400: 'Bad Request'
    },
    tags=['Insurer']
)
@api_view(['POST'])
def login_insurer(request) -> Response:
    """
    Log insurer into the system by returning refresh tokens
    :param request:
    :return: Response[access_token, refresh_token]
    """
    serializer_class = LoginInsurerSerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

    insurer_name = serializer_class.validated_data.get('username')
    password = serializer_class.validated_data.get('password')

    try:
        user = authenticate(username=insurer_name, password=password)
        if user is None:
            return Response({
                "message": "Failed to authenticate user"
            }, status=status.HTTP_400_BAD_REQUEST)

        # TODO: Fix login functionality
        # login(request, user)

        insurer = Insurer.objects.get(username=insurer_name)
        auth_token = RefreshToken.for_user(insurer)

        message = {
            "login_status": True,
            "access_token": str(auth_token.access_token),
            "refresh_token": str(auth_token)
        }
        return Response(message, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({f"The error {e.__str__()} occurred"}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='GET',
    operation_description='Request New OTP',
    responses={
        200: 'OK',
        400: 'Bad Request'
    },
    tags=['Insurer']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def request_new_otp(request):
    try:
        user = request.user
        insurer = Insurer.objects.get(username=user)

        send_otp(request, insurer_email=insurer.email)

        return Response({
            "message": "New OTP sent out!"
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            f"The error '{e}' occurred"
        }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    request_body=OTPSerializer,
    operation_description='Verify OTP',
    responses={
        200: 'OK',
        400: 'Bad Request'
    },
    tags=['Insurer']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_otp_token(request) -> Response:
    """
    Verify OTP endpoint
    :param request:
    :return: Response
    """

    serializer_class = OTPSerializer(data=request.data)
    user = request.user

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
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
    request_body=VerifyInsurerSerializer,
    operation_description='Verify Insurer',
    responses={
        200: 'OK',
        400: 'Bad Request'
    },
    tags=['Insurer']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_insurer(request) -> Response:
    """
    Request new OTP with the new_otp class instance
    :param request:
    :return: Response
    """
    serializer_class = VerifyInsurerSerializer(data=request.data)
    user = request.user

    try:
        insurer = Insurer.objects.get(username=user)

        if insurer.is_verified:
            return Response({
                "message": "This insurer is already verified"
            }, status=status.HTTP_200_OK)

        if not serializer_class.is_valid():
            return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

        otp = serializer_class.validated_data.get('otp')
        if not verify_otp(request, otp):
            return Response({
                "message": "Invalid OTP, request for new OTP!"
            }, status=status.HTTP_400_BAD_REQUEST)

        insurer = Insurer.objects.get(username=user)
        insurer.is_verified = True
        insurer.save()

        return Response({
            "message": "New otp has been sent out!"
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({f"The error {e.__str__()} occurred"}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    operation_description='Send Verification OTP to Insurer Email',
    request_body=ForgotPasswordEmailSerializer,
    responses={
        200: 'OK',
        400: 'Bad Request'
    },
    tags=['Insurer']
)
@api_view(['POST'])
def forgot_password_email(request) -> Response:
    serializer_class = ForgotPasswordEmailSerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

    insurer_email = serializer_class.validated_data.get('email')

    try:
        insurer = Insurer.objects.get(email=insurer_email)
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
    request_body=ForgotPasswordResetSerializer,
    responses={
        200: 'OK',
        400: 'Bad Request'
    },
    tags=['Insurer']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_password(request) -> Response:
    serializer_class = ForgotPasswordResetSerializer(data=request.data)
    user = request.user

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

    new_password = serializer_class.validated_data.get('new_password')

    try:
        insurer = Insurer.objects.get(username=user)
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
