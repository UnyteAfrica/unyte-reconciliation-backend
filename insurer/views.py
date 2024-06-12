from dotenv import load_dotenv, find_dotenv
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializer import CreateInsurerSerializer, LoginInsurerSerializer, OTPSerializer
from rest_framework.response import Response
from .models import Insurer
from django.conf import settings
import pyotp

load_dotenv(find_dotenv())


class OTPHandler:
    """
    OTP handler class for generating and verifying OTP
    """
    def __init__(self) -> None:
        self.otp = pyotp.TOTP(pyotp.random_base32(), interval=120)

    def gen_otp(self) -> str:
        """
        Generate OTP
        :return: string
        """
        return f"OTP generated!! as: {self.otp.now()}"

    def verify_otp(self, otp: str) -> bool:
        """
        Verify OTP
        :param otp: string
        :return: string
        """
        is_valid = False
        if self.otp.verify(otp) is False:
            return is_valid
        is_valid = True
        return is_valid


"""
Generate OTP for insurers on registration
"""
OTP = OTPHandler()

"""
Generate new OTP for requesting otp endpoint /api/new-otp
"""
new_otp = OTPHandler()


def store_insurer_profile_pictures(profile_picture):
    """
    Store profile picture in GCP
    :param profile_picture: string
    :return: string
    """
    return


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
        send_mail(
            subject='Verification email',
            message=f'{OTP.gen_otp()}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.TO_EMAIL, insurer_email],
        )
        serializer_class.save()
        return Response({f"Account successfully created for insurer: {insurer_name}"}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({f"The error {e.__str__()} occurred"}, status=status.HTTP_400_BAD_REQUEST)


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

    try:
        insurer_name = serializer_class.validated_data.get('username')
        insurer = Insurer.objects.get(username=insurer_name)
        auth_token = RefreshToken.for_user(insurer)

        message = {
            "login_status": True,
            "access_token": str(auth_token.access_token),
            "refresh_token": str(auth_token)
        }
        return Response(message, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({f"The error {e.__str__()} occurred"}, status=status.HTTP_400_BAD_REQUEST)


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
        first_otp = serializer_class.validated_data.get('otp')
        recent_otp = serializer_class.validated_data.get('new_otp')

        if 'otp' in list(serializer_class.validated_data.keys()):
            if OTP.verify_otp(first_otp) is False:
                return Response({
                    "message": "Invalid OTP, request for new OTP!"
                }, status=status.HTTP_400_BAD_REQUEST)

            insurer = Insurer.objects.get(username=user)
            insurer.is_verified = True
            insurer.save()

            return Response({
                "message": "OTP verified"
            }, status=status.HTTP_200_OK)

        elif 'new_otp' in list(serializer_class.validated_data.keys()):
            if new_otp.verify_otp(recent_otp) is False:
                return Response({
                    "message": "Invalid OTP, request for new OTP!"
                }, status=status.HTTP_400_BAD_REQUEST)

            insurer = Insurer.objects.get(username=user)
            insurer.is_verified = True
            insurer.save()

            return Response({
                "message": "OTP verified"
            }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({f"The error {e.__str__()} occurred"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def request_new_otp(request) -> Response:
    """
    Request new OTP with the new_otp class instance
    :param request:
    :return: Response
    """
    user = request.user

    try:
        insurer = Insurer.objects.get(username=user)

        if insurer.is_verified:
            return Response({
                "message": "This insurer is already verified"
            }, status=status.HTTP_200_OK)

        send_mail(
            subject='Verification email',
            message=f'{new_otp.gen_otp()}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.TO_EMAIL, insurer.email],
        )
        return Response({
            "message": "New otp has been sent out!"
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({f"The error {e.__str__()} occurred"}, status=status.HTTP_400_BAD_REQUEST)
