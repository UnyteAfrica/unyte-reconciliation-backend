from datetime import datetime
import csv
from io import TextIOWrapper

from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import smart_bytes, DjangoUnicodeDecodeError, smart_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from dotenv import load_dotenv, find_dotenv
from drf_yasg import openapi
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

from agents.models import Agent
from policies.models import Policies, AgentPolicy, PolicyProductType
from .serializer import CreateInsurerSerializer, LoginInsurerSerializer, OTPSerializer, ForgotPasswordEmailSerializer, \
    ForgotPasswordResetSerializer, SendNewOTPSerializer, ViewInsurerDetails, AgentSerializer, \
    InsurerProfileSerializer, CustomAgentSerializer, \
    ValidateRefreshToken, CreatePolicies, UpdateProfileImageSerializer, CreateProductForPolicy, InsurerViewAllPolicies, \
    InsurerViewAllProducts, UploadCSVFileSerializer
from .response_serializers import SuccessfulCreateInsurerSerializer, SuccessfulLoginInsurerSerializer, \
    SuccessfulSendNewOTPSerializer, SuccessfulVerifyOTPSerializer, SuccessfulForgotPasswordSerializer, \
    SuccessfulResetPasswordSerializer, SuccessfulRefreshAccessTokenSerializer, SuccessfulPasswordTokenCheckSerializer, \
    SuccessfulViewInsurerSerializer, SuccessfulListAllAgentsSerializer, SuccessfulInsurerProductsSerializer, \
    SuccessfulInsurerPoliciesSerializer, SuccessfulInsurerAgentSignupSerializer, SuccessfulCreateProductSerializer, \
    SuccessfulCreateProductForPolicySerializer, SuccessfulInsurerAgentSignupCSVSerializer
from rest_framework.response import Response
from .models import Insurer, InsurerProfile
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings
from .utils import generate_otp, verify_otp, gen_absolute_url, gen_sign_up_url_for_agent

load_dotenv(find_dotenv())


@swagger_auto_schema(
    method='POST',
    request_body=CreateInsurerSerializer,
    operation_description="Create new insurer",
    responses={
        201: openapi.Response(
            'Created',
            SuccessfulCreateInsurerSerializer
        ),
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

        current_year = datetime.now().year
        company_name = insurer.business_name
        context = {
            "current_year": current_year,
            "company_name": company_name,

        }

        html_message = render_to_string('welcome.html', context)

        send_mail(
            subject='Welcome email',
            message=f'Welcome',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.TO_EMAIL, insurer_email],
            html_message=html_message
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
        200: openapi.Response(
            'OK',
            SuccessfulLoginInsurerSerializer
        ),
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
                "message": "Failed to authenticate insurer"
            }, status=status.HTTP_400_BAD_REQUEST)

        insurer = Insurer.objects.get(email=email)

        otp = generate_otp()
        insurer.otp = otp
        insurer.otp_created_at = datetime.now().time()

        insurer.save()

        current_year = datetime.now().year
        company_name = insurer.business_name
        context = {
            "current_year": current_year,
            "company_name": company_name,
            "otp": otp
        }

        html_message = render_to_string('otp.html', context)

        send_mail(
            subject='Login OTP',
            message=f'{otp}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.TO_EMAIL, email],
            html_message=html_message
        )
        message = {
            "message": "OTP has been sent out to your email"
        }
        return Response(message, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({f"The error {e.__str__()} occurred"}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    request_body=SendNewOTPSerializer,
    operation_description='Sends new OTP to Insurer email',
    responses={
        200: openapi.Response(
            'OK',
            SuccessfulSendNewOTPSerializer
        ),
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

    current_year = datetime.now().year
    company_name = insurer.business_name
    context = {
        "current_year": current_year,
        "company_name": company_name,
        "otp": otp
    }

    html_message = render_to_string('otp.html', context)

    send_mail(
        subject='Request New OTP',
        message=f'{otp}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.TO_EMAIL, insurer_email],
        html_message=html_message
    )

    return Response({
        "message": "New OTP sent out!"
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='POST',
    request_body=OTPSerializer,
    operation_description='Verifies Insurer OTP Token',
    responses={
        200: openapi.Response(
            'OK',
            SuccessfulVerifyOTPSerializer
        ),
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
    operation_description='Send Verification OTP to Insurer Email',
    request_body=ForgotPasswordEmailSerializer,
    responses={
        200: openapi.Response(
            'OK',
            SuccessfulForgotPasswordSerializer
        ),
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
        current_year = datetime.now().year
        company_name = insurer.business_name

        context = {
            'id': id_base64,
            'token': token,
            'current_year': current_year,
            'company_name': company_name
        }

        html_message = render_to_string('forgot-password.html', context=context)

        send_mail(
            subject='Forgot Password',
            message=f'{abs_url}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.TO_EMAIL, insurer_email],
            html_message=html_message
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
    operation_description='Resets Insurer forgotten password',
    request_body=ForgotPasswordResetSerializer,
    responses={
        200: openapi.Response(
            'OK',
            SuccessfulResetPasswordSerializer,
        ),
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
    method='POST',
    operation_description='Returns a new access token from a valid refresh token',
    request_body=ValidateRefreshToken,
    responses={
        200: openapi.Response(
            'OK',
            SuccessfulRefreshAccessTokenSerializer,
        ),
        400: 'Bad Request'
    },
    tags=['Insurer']
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
    operation_description='ID and Token Verification',
    responses={
        200: openapi.Response(
            'OK',
            SuccessfulPasswordTokenCheckSerializer,
        ),
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
    operation_description='View Insurer details',
    responses={
        200: openapi.Response(
            'OK',
            SuccessfulViewInsurerSerializer,
        ),
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
    operation_description='View all agents invited by an Insurer',
    responses={
        200: openapi.Response(
            'OK',
            SuccessfulListAllAgentsSerializer(many=True),
        ),
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
    method='GET',
    operation_description='Returns a list of all products (unsold policies) created by an Insurer',
    responses={
        200: openapi.Response(
            'OK',
            SuccessfulInsurerProductsSerializer(many=True),
        ),
        400: 'Bad Request',
        404: 'Not Found'
    },
    tags=['Insurer']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_products(request):
    insurer_id = request.user.id
    paginator = PageNumberPagination()
    paginator.page_size = 10

    insurer = get_object_or_404(Insurer, id=insurer_id)
    policies_queryset = Policies.objects.filter(insurer=insurer)

    all_policies = []
    for policy in policies_queryset:
        policy_product_types_queryset = PolicyProductType.objects.filter(policy=policy)
        for policy_product_type in policy_product_types_queryset:
            res = {'product': policy.name,
                   'product_category': policy.policy_category,
                   'valid_from': policy.valid_from,
                   'valid_to': policy.valid_to
                   }
            if policy_product_type.policy.name == policy.name:
                # print(policy_product_type.name)
                res["name"] = policy_product_type.name
                res["premium"] = str(policy_product_type.premium)
                res["flat_fee"] = policy_product_type.flat_fee

                all_policies.append(res)
    result_qs = paginator.paginate_queryset(all_policies, request)
    return paginator.get_paginated_response(result_qs)


# TODO: Check out this logic
@swagger_auto_schema(
    method='GET',
    operation_description='Returns a list of all policies (sold products) sold by agents under an Insurer',
    responses={
        200: openapi.Response(
            'OK',
            SuccessfulInsurerPoliciesSerializer(many=True),
        ),
        400: 'Bad Request',
        404: 'Not Found'
    },
    tags=['Insurer']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_policies(request):
    insurer_id = request.user.id
    paginator = PageNumberPagination()
    paginator.page_size = 10

    # insurer = get_object_or_404(Insurer, id=insurer_id)
    agents = Agent.objects.filter(affiliated_company=insurer_id)

    agent_sold_policies = []
    number_of_policies = 0

    for agent in agents:
        queryset = AgentPolicy.objects.filter(agent=agent)
        number_of_policies += len(queryset)
        for policy_type in queryset:
            res = {'agent': f"{agent.first_name} {agent.last_name}",
                   'policy_name': policy_type.product_type.policy.name,
                   'policy_category': policy_type.product_type.policy.policy_category,
                   "name": policy_type.product_type.name, "premium": policy_type.product_type.premium,
                   "flat_fee": policy_type.product_type.flat_fee, 'date_sold': policy_type.date_sold}

            agent_sold_policies.append(res)
    result_page = paginator.paginate_queryset(agent_sold_policies, request)
    return paginator.get_paginated_response(result_page)


@swagger_auto_schema(
    method='POST',
    operation_description='Generate SignUp Link for Agents',
    request_body=CustomAgentSerializer,
    responses={
        200: openapi.Response(
            'OK',
            SuccessfulInsurerAgentSignupSerializer,
        ),
        400: 'Bad Request',
        404: 'Not Found'
    },
    tags=['Insurer']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def invite_agents(request):
    serializer_class = CustomAgentSerializer(data=request.data)
    insurer_id = request.user.id
    insurer = get_object_or_404(Insurer, pk=insurer_id)

    unyte_unique_insurer_id = insurer.unyte_unique_insurer_id

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)

    agent_list = serializer_class.validated_data.get('agents_list')
    email_recipients = []

    relative_link = reverse('agents:register_agent')
    relative_link = relative_link.replace('/api/', '/')
    link = gen_sign_up_url_for_agent(relative_link, unyte_unique_insurer_id)

    current_year = datetime.now().year
    company_name = insurer.business_name

    for agent in agent_list:
        name = agent['names']
        email = agent['emails']

        context = {
            "current_year": current_year,
            "company_name": company_name,
            "unyte_unique_insurer_id": unyte_unique_insurer_id,
            "name": name
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
            html_message=html_message
        )
        email_recipients.pop(0)

    return Response({
        "message": f"Link generated: {link}"
    })


@swagger_auto_schema(
    method='POST',
    operation_description='Generate SignUp Link for Agents through CSV file',
    responses={
        200: openapi.Response(
            'OK',
            SuccessfulInsurerAgentSignupCSVSerializer,
        ),
        400: 'Bad Request',
        404: 'Not Found'
    },
    tags=['Insurer']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def invite_agents_csv(request):
    serializer_class = UploadCSVFileSerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)

    insurer_id = request.user.id
    insurer = get_object_or_404(Insurer, pk=insurer_id)
    unyte_unique_insurer_id = insurer.unyte_unique_insurer_id
    company_name = insurer.business_name
    current_year = datetime.now().year

    relative_link = reverse('agents:register_agent')
    relative_link = relative_link.replace('/api/', '/')
    link = gen_sign_up_url_for_agent(relative_link, unyte_unique_insurer_id)

    try:
        otp = serializer_class.validated_data.get('otp')

        if otp != insurer.otp:
            return Response({
                "error": "Invalid OTP"
            }, status.HTTP_400_BAD_REQUEST)

        otp_created_time = insurer.otp_created_at
        verify = verify_otp(otp_created_time)

        if not verify:
            message = {
                'error': 'OTP has expired'
            }
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['agents_csv']
        file_extension = file.name.split('.')[-1]
        if file_extension != 'csv':
            return Response({
                "error": f"Unacceptable file format {file_extension}. Must be a csv file"
            }, status.HTTP_400_BAD_REQUEST)
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
                    "current_year": current_year,
                    "company_name": company_name,
                    "unyte_unique_insurer_id": unyte_unique_insurer_id,
                    "name": agent_name
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
                    html_message=html_message
                )
        return Response({
            "message": f"Successfully sent out invite links to {len(all_rows) - 1} agent(s)"
        })
    except Exception as e:
        return Response({
            "error": f"{e.__str__()}"
        }, status.HTTP_400_BAD_REQUEST)


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

    data = {
        'email': insurer_email,
        'business_name': insurer_business_name,
        'profile_image': str(insurer_profile_pic)
    }

    serializer_class = InsurerProfileSerializer(data=data)

    if not serializer_class.is_valid():
        return Response({
            "error": serializer_class.errors
        }, status.HTTP_400_BAD_REQUEST)

    return Response(serializer_class.data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='POST',
    operation_description='Create Product',
    request_body=CreatePolicies,
    responses={
        200: openapi.Response(
            'OK',
            SuccessfulCreateProductSerializer,
        ),
        400: 'Bad Request',
        404: 'Not Found'
    },
    tags=['Insurer']
)
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def create_product(request) -> Response:
    insurer_id = request.user.id
    insurer = get_object_or_404(Insurer, pk=insurer_id)
    serializer_class = CreatePolicies(data=request.data)
    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)

    policy_name = serializer_class.validated_data.get('name')
    policies = Policies.objects.filter(insurer=insurer)
    all_policy_names = [policy.name for policy in policies]

    if policy_name in all_policy_names:
        existing_policy = Policies.objects.get(name=policy_name)
        return Response({
            "error": f"Product with name {policy_name} already exists",
            "product_id": f"{existing_policy.id}"
        }, status.HTTP_400_BAD_REQUEST)

    try:
        policy = Policies.objects.create(**serializer_class.validated_data, insurer=insurer)
        policy.save()
        res = {
            "id": policy.id,
            "policy": policy.name,
            "policy_category": policy.policy_category,
            "valid_from": policy.valid_from,
            "valid_to": policy.valid_to
        }

        policy_types = []
        policy_type_objs = PolicyProductType.objects.filter(policy=policy)

        for policy_type in policy_type_objs:
            policy_types.append({
                "type": policy_type.name,
                "premium": policy_type.premium,
                "flat_fee": policy_type.flat_fee
            })
        res['policy_types'] = policy_types

        return Response(res, status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "error": f"The error '{e}' occurred"
        }, status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    operation_description='Create Product for Policy',
    request_body=CreateProductForPolicy,
    responses={
        200: openapi.Response(
            'OK',
            SuccessfulCreateProductForPolicySerializer,
        ),
        400: 'Bad Request',
        404: 'Not Found'
    },
    tags=['Insurer']
)
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def create_products_for_policy(request, policy_id) -> Response:
    serializer_class = CreateProductForPolicy(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)

    try:
        policy = get_object_or_404(Policies, pk=policy_id)
        all_product_types = [product_type.name for product_type in PolicyProductType.objects.all()]
        product_type_name = serializer_class.validated_data.get('name')

        if product_type_name in all_product_types:
            return Response({
                "error": f"An existing product type for this product with name {product_type_name} already exists"
            }, status.HTTP_400_BAD_REQUEST)

        product_policy = PolicyProductType.objects.create(policy=policy, **serializer_class.data)
        product_policy.save()

        return Response({
            "message": f"A new product has been added to {policy.name}"
        }, status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "error": f"The error '{e}' occurred"
        }, status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='GET',
    operation_description='View products an agent has sold',
    responses={
        200: openapi.Response(
            'OK',
            SuccessfulInsurerPoliciesSerializer,
        ),
        400: 'Bad Request',
        404: 'Not Found'
    },
    tags=['Insurer']
)
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def view_products_an_agent_has_sold(request, agent_id: int):
    # insurer = get_object_or_404(Insurer, id=insurer_id)
    agent = get_object_or_404(Agent, pk=agent_id)
    paginator = PageNumberPagination()
    paginator.page_size = 10

    agent_sold_policies = []

    queryset = AgentPolicy.objects.filter(agent=agent)
    for policy_type in queryset:
        res = {'agent': f"{agent.first_name} {agent.last_name}", 'policies_sold': [],
               'policy_name': policy_type.product_type.policy.name,
               'policy_category': policy_type.product_type.policy.policy_category,
               "name": policy_type.product_type.name,
               "premium": policy_type.product_type.premium,
               "flat_fee": policy_type.product_type.flat_fee,
               "date_sold": policy_type.date_sold
               }

        agent_sold_policies.append(res)
    result_page = paginator.paginate_queryset(agent_sold_policies, request)
    return paginator.get_paginated_response(result_page)


@swagger_auto_schema(
    method='GET',
    manual_parameters=[
        openapi.Parameter('start_date',
                          openapi.IN_QUERY,
                          description="start date for date range",
                          type=openapi.TYPE_STRING),
        openapi.Parameter('end_date',
                          openapi.IN_QUERY,
                          description="end date for date range",
                          type=openapi.TYPE_STRING),
    ],
    operation_description='View products agents sold in a date range',
    responses={
        200: openapi.Response(
            'OK',
            SuccessfulInsurerPoliciesSerializer,
        ),
        400: 'Bad Request',
        404: 'Not Found'
    },
    tags=['Insurer']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_sold_products_with_date_params(request) -> Response:
    insurer_id = request.user.id
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    paginator = PageNumberPagination()
    paginator.page_size = 10

    try:
        agents = Agent.objects.filter(affiliated_company=insurer_id)

        agent_sold_policies = []

        for agent in agents:
            queryset = AgentPolicy.objects.filter(agent=agent, date_sold__range=[start_date, end_date])
            for policy_type in queryset:
                res = {'agent': f"{agent.first_name} {agent.last_name}",
                       'policy_name': policy_type.product_type.policy.name,
                       'policy_category': policy_type.product_type.policy.policy_category,
                       "name": policy_type.product_type.name,
                       "premium": policy_type.product_type.premium,
                       "flat_fee": policy_type.product_type.flat_fee,
                       'date_sold': policy_type.date_sold
                       }
                agent_sold_policies.append(res)
        result_page = paginator.paginate_queryset(agent_sold_policies, request)
        return paginator.get_paginated_response(result_page)
    except Exception as e:
        return Response({
            "error": f"The error {e} occurred"
        }, status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    operation_description='Create Policy',
    request_body=UpdateProfileImageSerializer,
    responses={
        200: 'OK',
        400: 'Bad Request',
        404: 'Not Found'
    },
    tags=['Insurer']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_profile_image(request) -> Response:
    insurer = get_object_or_404(Insurer, pk=request.user.id)
    insurer_profile_obj = get_object_or_404(InsurerProfile, insurer=insurer)
    serializer_class = UpdateProfileImageSerializer(insurer_profile_obj, data=request.data, partial=True)
    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)

    serializer_class.save()
    return Response({
        "message": "Profile image updated"
    }, status.HTTP_200_OK)
