import json
import os
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.encoding import smart_bytes, DjangoUnicodeDecodeError, smart_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from dotenv import load_dotenv, find_dotenv
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status

from policies.models import InsurerPolicy, Policies
from .serializer import CreateInsurerSerializer, LoginInsurerSerializer, OTPSerializer, ForgotPasswordEmailSerializer, \
    ForgotPasswordResetSerializer, SendNewOTPSerializer, ViewInsurerDetails, AgentSerializer, \
    InsurerClaimSellPolicySerializer, InsurerViewAllPolicies, TestViewInsurerProfile
from rest_framework.response import Response
from .models import Insurer, InsurerProfile
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings
from .utils import generate_otp, verify_otp, gen_absolute_url, gen_sign_up_url_for_agent

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
        business_name = serializer_class.validated_data.get('business_name')
        insurer_email = serializer_class.validated_data.get('email')

        """
        Send email to insurer including otp.
        """
        serializer_class.save()
        insurer = Insurer.objects.get(email=insurer_email)
        otp = insurer.otp

        send_mail(
            subject='Verification email',
            message=f'{otp}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.TO_EMAIL, insurer_email],
        )

        message = {
            'id': insurer.id,
            "message": f"Account successfully created for user: {business_name}"
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

    email = serializer_class.validated_data.get('email')
    password = serializer_class.validated_data.get('password')

    try:
        user = authenticate(email=email, password=password)
        if user is None:
            return Response({
                "message": "Failed to authenticate user"
            }, status=status.HTTP_400_BAD_REQUEST)

        insurer = Insurer.objects.get(email=email)
        print(login(request, insurer))
        auth_token = RefreshToken.for_user(insurer)

        message = {
            "login_status": True,
            'id': insurer.id,
            "access_token": str(auth_token.access_token),
            "refresh_token": str(auth_token)
        }
        return Response(message, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({f"The error {e.__str__()} occurred"}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    request_body=SendNewOTPSerializer,
    operation_description='Request New OTP',
    responses={
        200: 'OK',
        400: 'Bad Request'
    },
    tags=['Insurer']
)
@api_view(['POST'])
def request_new_otp(request):
    serializer_class = SendNewOTPSerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

    insurer_email = serializer_class.validated_data.get('email')

    if not Insurer.objects.filter(email=insurer_email).exists():
        return Response({
            "message": f"Email: {insurer_email} does not exists"
        }, status=status.HTTP_400_BAD_REQUEST)

    insurer = Insurer.objects.get(email=insurer_email)

    otp = generate_otp()
    insurer.otp = otp
    insurer.otp_created_at = datetime.now().time()

    insurer.save()

    send_mail(
        subject='Verification email',
        message=f'{otp}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.TO_EMAIL, insurer_email],
    )

    return Response({
        "message": "New OTP sent out!"
    }, status=status.HTTP_200_OK)


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
@permission_classes([AllowAny])
def verify_otp_token(request) -> Response:
    """
    Verify OTP endpoint
    :param request:
    :return: Response
    """
    serializer_class = OTPSerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        insurer_email = serializer_class.validated_data.get('email')
        otp = serializer_class.validated_data.get('otp')

        insurer = Insurer.objects.get(email=insurer_email)

        insurer_otp = insurer.otp

        if insurer_otp != otp:
            message = {
                "error": "Incorrect OTP"
            }
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        otp_created_time = insurer.otp_created_at
        verify = verify_otp(otp_created_time)

        if not verify:
            message = {
                'error': 'OTP has expired'
            }
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": "OTP Verified"
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
        id_base64 = urlsafe_base64_encode(smart_bytes(insurer.id))
        token = PasswordResetTokenGenerator().make_token(insurer)
        abs_url = gen_absolute_url(id_base64, token)

        send_mail(
            subject='Verification email',
            message=f'{abs_url}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.TO_EMAIL, insurer_email],
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
def reset_password(request) -> Response:
    serializer_class = ForgotPasswordResetSerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "message": "Password successfully updated"
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='GET',
    operation_description='Id and Token Verification',
    responses={
        200: 'OK',
        400: 'Bad Request'
    },
    tags=['Insurer']
)
@api_view(['GET'])
def password_token_check(request, id_base64, token):
    try:
        insurer_id = smart_str(urlsafe_base64_decode(id_base64))
        insurer = Insurer.objects.get(id=insurer_id)

        if not PasswordResetTokenGenerator().check_token(insurer, token):
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
    method='GET',
    operation_description='View Insurer Details',
    responses={
        200: 'OK',
        400: 'Bad Request'
    },
    tags=['Insurer']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_insurer(request):
    insurer_id = request.user.id
    insurer = get_object_or_404(Insurer, pk=insurer_id)
    serializer_class = ViewInsurerDetails(insurer)

    return Response(serializer_class.data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='GET',
    operation_description='View All Agents For Insurer',
    responses={
        200: 'OK',
        403: 'Unauthorized',
        404: 'Not Found',
        400: 'Bad Request'
    },
    tags=['Insurer']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_all_agents_for_insurer(request):
    insurer_id = request.user.id

    insurer = get_object_or_404(Insurer, pk=insurer_id)
    query_set = insurer.agent_set.all()
    serializer_class = AgentSerializer(query_set, many=True)

    return Response(serializer_class.data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='POST',
    operation_description='Agent Claim Policy',
    request_body=InsurerClaimSellPolicySerializer,
    responses={
        200: 'OK',
        400: 'Bad Request',
        404: 'Not Found'
    },
    tags=['Insurer']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def insurer_sell_policy(request):
    insurer_id = request.user.id
    serializer_class = InsurerClaimSellPolicySerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response({
            serializer_class.errors
        }, status.HTTP_400_BAD_REQUEST)

    try:
        policy_name = serializer_class.validated_data.get('policy_name')
        insurer = Insurer.objects.get(id=insurer_id)
        policy = Policies.objects.get(name=policy_name)
        claim_policy = InsurerPolicy.objects.get(insurer=insurer, policy=policy)

        if claim_policy.is_sold is True:
            return Response({
                "error": "You have already sold this policy"
            }, status.HTTP_400_BAD_REQUEST)

        claim_policy.is_sold = True
        claim_policy.save()

        return Response({
            "message": "You have successfully sold this policy"
        }, status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "error": f"The error '{e}' occurred"
        }, status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    operation_description='Agent Claim Policy',
    request_body=InsurerClaimSellPolicySerializer,
    responses={
        200: 'OK',
        400: 'Bad Request',
        404: 'Not Found'
    },
    tags=['Insurer']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def insurer_claim_policy(request):
    insurer_id = request.user.id
    serializer_class = InsurerClaimSellPolicySerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response({
            serializer_class.errors
        }, status.HTTP_400_BAD_REQUEST)

    try:
        policy_name = serializer_class.validated_data.get('policy_name')
        insurer = Insurer.objects.get(id=insurer_id)
        policy = Policies.objects.get(name=policy_name)

        if Insurer.objects.filter(insurer=insurer, policy=policy).exists():
            return Response({
                "error": "You have claimed this policy already"
            }, status.HTTP_400_BAD_REQUEST)

        claim_policy = InsurerPolicy.objects.create(insurer=insurer, policy=policy)

        claim_policy.save()
        return Response({
            "message": "You have claimed a new policy"
        }, status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "error": f"The error '{e}' occurred"
        }, status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='GET',
    operation_description='Agent Claim Policy',
    responses={
        200: 'OK',
        400: 'Bad Request',
        404: 'Not Found'
    },
    tags=['Insurer']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_policies(request):
    insurer_id = request.user.id
    insurer = get_object_or_404(Insurer, id=insurer_id)

    queryset = insurer.get_policies()
    serializer_class = InsurerViewAllPolicies(queryset, many=True)

    return Response(serializer_class.data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='GET',
    operation_description='Sold Policies',
    responses={
        200: 'OK',
        400: 'Bad Request',
        404: 'Not Found'
    },
    tags=['Insurer']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_sold_policies(request):
    insurer_id = request.user.id

    insurer = get_object_or_404(Insurer, id=insurer_id)
    queryset = insurer.get_sold_policies()
    serializer_class = InsurerViewAllPolicies(queryset, many=True)

    return Response(serializer_class.data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='GET',
    operation_description='Generate SignUp Link for Insurer',
    responses={
        200: 'OK',
        400: 'Bad Request',
        404: 'Not Found'
    },
    tags=['Insurer']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_sign_up_link_for_agent(request):
    insurer_id = request.user.id
    insurer = get_object_or_404(Insurer, pk=insurer_id)

    unyte_unique_insurer_id = insurer.unyte_unique_insurer_id

    relative_link = reverse('agents:register_agent')
    relative_link = relative_link.replace('/api/', '/')
    link = gen_sign_up_url_for_agent(relative_link, unyte_unique_insurer_id)

    return Response({
        "message": f"Link generated: {link}"
    })


# TODO: Review the functionality with Seun.
@swagger_auto_schema(
    method='GET',
    operation_description='View Insurer Profile',
    responses={
        200: 'OK',
        400: 'Bad Request',
        404: 'Not Found'
    },
    tags=['Insurer']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_insurer_profile(request) -> Response:
    insurer_id = request.user.id

    insurer = get_object_or_404(Insurer, pk=insurer_id)
    insurer_profile = get_object_or_404(InsurerProfile, insurer=insurer)

    insurer_email = insurer.email
    insurer_business_name = insurer.business_name
    insurer_profile_pic = insurer_profile.profile_image.url
    print(insurer_profile_pic)

    data = {
        'email': insurer_email,
        'business_name': insurer_business_name,
        'profile_image': str(insurer_profile_pic)
    }

    serializer_class = TestViewInsurerProfile(data=data)

    if not serializer_class.is_valid():
        return Response({
            "error": serializer_class.errors
        }, status.HTTP_400_BAD_REQUEST)

    return Response(serializer_class.data, status.HTTP_200_OK)