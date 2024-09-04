from datetime import datetime
from pprint import pprint

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError, smart_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from insurer.models import Insurer
from policies.models import Policies, AgentPolicy, PolicyProductType
from .models import Agent, AgentProfile
from .serializer import CreateAgentSerializer, LoginAgentSerializer, AgentSendNewOTPSerializer, AgentOTPSerializer, \
    AgentForgotPasswordEmailSerializer, AgentForgotPasswordResetSerializer, ViewAgentDetailsSerializer, \
    AgentClaimPolicySerializer, AgentSellPolicySerializer, AgentViewAllClaimedPolicies, \
    ViewAgentProfile, LogoutAgentSerializer, AgentValidateRefreshToken
from .utils import generate_otp, verify_otp, gen_absolute_url, generate_unyte_unique_agent_id


@swagger_auto_schema(
    method='POST',
    manual_parameters=[
        openapi.Parameter('invite',
                          openapi.IN_QUERY,
                          description="Insurer unique unyte id",
                          type=openapi.TYPE_STRING),
    ],
    request_body=CreateAgentSerializer,
    operation_description='Create New Agent',
    responses={
        '201': 'Created',
        '400': 'Bad Request'
    },
    tags=['Agent']
)
@api_view(['POST'])
def create_agent(request) -> Response:
    serializer_class = CreateAgentSerializer(data=request.data)

    if request.query_params.get('invite') is None:
        return Response({
            "error": "Can't find your Insurer's identifier"
        }, status.HTTP_400_BAD_REQUEST)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        agent_email = serializer_class.validated_data.get('email')
        uuid = request.query_params.get('invite')

        insurer = Insurer.objects.get(unyte_unique_insurer_id=uuid)

        agent_data = serializer_class.validated_data
        agent_data['affiliated_company'] = insurer

        first_name = agent_data.get("first_name")
        last_name = agent_data.get("last_name")
        bank_account = agent_data.get('bank_account')

        uuad = generate_unyte_unique_agent_id(first_name, bank_account)

        agent = Agent.objects.create_user(**agent_data,
                                          unyte_unique_agent_id=uuad,
                                          otp=generate_otp(),
                                          otp_created_at=datetime.now().time())
        agent.save()

        agent = Agent.objects.get(email=agent_email)
        current_year = datetime.now().year

        context = {
            "current_year": current_year,
            "name": f"{first_name} {last_name}"
        }
        html_message = render_to_string('agents/welcome.html', context=context)
        plain_html_message = strip_tags(html_message)

        send_mail(
            subject='Welcome email',
            message=plain_html_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.TO_EMAIL, agent_email],
            html_message=html_message
        )

        message = {
            'id': agent.id,
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

        otp = generate_otp()
        agent.otp = otp
        agent.otp_created_at = datetime.now().time()

        name = f"{agent.first_name} {agent.last_name}"
        current_year = datetime.now().year

        agent.save()

        context = {
            "name": name,
            "current_year": current_year,
            "otp": otp
        }

        html_message = render_to_string("agents/otp.html", context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject='Login OTP',
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.TO_EMAIL, agent_email],
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
    name = f"{agent.first_name} {agent.last_name}"
    current_year = datetime.now().year

    agent.save()

    context = {
        "name": name,
        "current_year": current_year,
        "otp": otp
    }

    html_message = render_to_string("agents/otp.html", context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject='Request New OTP',
        message=plain_message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.TO_EMAIL, agent_email],
        html_message=html_message
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
    operation_description='Send Verification OTP to Agent Email',
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

    agent = get_object_or_404(Agent, email=serializer_class.validated_data.get('email'))

    agent_email = serializer_class.validated_data.get('email')

    try:
        id_base64 = urlsafe_base64_encode(smart_bytes(agent.id))
        token = PasswordResetTokenGenerator().make_token(agent)
        absolute_url = gen_absolute_url(id_base64, token)
        name = f"{agent.first_name} + {agent.last_name}"

        context = {
            "agent_name": name,
            "url": absolute_url,
            "id": id_base64,
            "token": token,
            "current_year": datetime.now().year
        }

        html_message = render_to_string('agents/forgot-password.html', context=context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject='Forgot Password',
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.TO_EMAIL, agent_email],
            html_message=html_message
        )

        response = {
            "message": "Confirmation email sent"
        }
        return Response(response, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "error": f"{e}"
        }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='GET',
    operation_description='ID and Token Verification',
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
    operation_description="Resets Agent's forgotten password",
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
    method='POST',
    operation_description='Returns a new access token from a valid refresh token',
    request_body=AgentValidateRefreshToken,
    responses={
        200: 'OK',
        400: 'Bad Request'
    },
    tags=['Agent']
)
@api_view(['POST'])
def refresh_access_token(request):
    serializer_class = AgentValidateRefreshToken(data=request.data)

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
def view_agent_details(request):
    agent_id = request.user.id
    agent = get_object_or_404(Agent, pk=agent_id)
    serializer_class = ViewAgentDetailsSerializer(agent)

    return Response(serializer_class.data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='POST',
    operation_description='Agents sell products',
    request_body=AgentSellPolicySerializer,
    responses={
        200: 'OK',
        400: 'Bad Request',
        404: 'Not Found'
    },
    tags=['Agent']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def agent_sell_product(request):
    agent_id = request.user.id
    serializer_class = AgentSellPolicySerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response({
            serializer_class.errors
        }, status.HTTP_400_BAD_REQUEST)

    policy_name = serializer_class.validated_data.get('policy_name')
    policy_obj = get_object_or_404(Policies, name=policy_name)

    available_product_types_objs = PolicyProductType.objects.filter(policy=policy_obj)
    available_product_types = [
        {"name": product.name,
         "premium": product.premium,
         "flat_fee": product.flat_fee, }

        for product in available_product_types_objs
    ]

    agent = get_object_or_404(Agent, pk=agent_id)
    product_types = serializer_class.validated_data.get('product_type')
    pprint(product_types)

    for product_type in product_types:
        if product_type not in available_product_types:
            return Response({
                "error": f"Invalid product type for product: {policy_name}"
            }, status.HTTP_400_BAD_REQUEST)

        product_type_obj = get_object_or_404(PolicyProductType, name=product_type.get('name'),
                                             premium=product_type.get('premium'),
                                             flat_fee=product_type.get('flat_fee'))
        agent_policy = AgentPolicy.objects.create(agent=agent, product_type=product_type_obj)
        agent_policy.save()

    if len(product_types) > 1:
        return Response({
            "message": "You have successfully sold these product"
        }, status.HTTP_200_OK)

    return Response({
        "message": "You have successfully sold this product"
    }, status.HTTP_200_OK)




@swagger_auto_schema(
    method='GET',
    operation_description='Returns a list of policies (sold products)',
    responses={
        200: 'OK',
        400: 'Bad Request',
        404: 'Not Found'
    },
    tags=['Agent']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_policies(request):
    agent_id = request.user.id
    agent = get_object_or_404(Agent, id=agent_id)
    queryset = AgentPolicy.objects.filter(agent=agent)

    policies = []
    for agent_policy in queryset:
        res = {
            'policy_name': agent_policy.product_type.policy.name,
            'policy_category': agent_policy.product_type.policy.policy_category,
            "date_sold": agent_policy.date_sold,
            'product_type': {
                "name": agent_policy.product_type.name,
                "premium": agent_policy.product_type.premium,
                "flat_fee": agent_policy.product_type.flat_fee,
            }
        }
        policies.append(res)
    policies.append({
        "number_of_sold_policies": len(queryset)
    })
    return Response(policies, status.HTTP_200_OK)


@swagger_auto_schema(
    method='GET',
    operation_description='View Agent Profile',
    responses={
        200: 'OK',
        400: 'Bad Request',
        404: 'Not Found'
    },
    tags=['Agent']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_agent_profile(request) -> Response:
    agent_id = request.user.id

    agent = get_object_or_404(Agent, pk=agent_id)
    agent_profile = get_object_or_404(AgentProfile, agent=agent)

    agent_email = agent.email
    agent_first_name = agent.first_name
    agent_last_name = agent.last_name
    agent_middle_name = agent.middle_name
    agent_profile_pic = agent_profile.profile_image.url

    data = {
        'email': agent_email,
        'first_name': agent_first_name,
        'last_name': agent_last_name,
        'middle_name': agent_middle_name,
        'profile_image': str(agent_profile_pic)
    }

    serializer_class = ViewAgentProfile(data=data)

    if not serializer_class.is_valid():
        return Response({
            "error": serializer_class.errors
        }, status.HTTP_400_BAD_REQUEST)

    return Response(serializer_class.data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='GET',
    operation_description='Returns a list of all products (unsold policies) by agent insurer',
    responses={
        200: 'OK',
        400: 'Bad Request',
        404: 'Not Found'
    },
    tags=['Agent']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_products(request) -> Response:
    agent_id = request.user.id
    agent = get_object_or_404(Agent, pk=agent_id)
    insurer = agent.affiliated_company

    policies_queryset = Policies.objects.filter(insurer=insurer)

    all_policies = []
    for policy in policies_queryset:
        policy_product_types = []
        res = {'policy': policy.name,
               'policy_category': policy.policy_category,
               'valid_from': policy.valid_from,
               'valid_to': policy.valid_to}

        policy_product_types_queryset = PolicyProductType.objects.filter(policy=policy)
        for policy_product_type in policy_product_types_queryset:
            if policy_product_type.policy.name == policy.name:
                policy_product_types.append({
                    "name": policy_product_type.name,
                    "premium": policy_product_type.premium,
                    "flat_fee": policy_product_type.flat_fee,
                })
            else:
                print(policy.name)
        res['policy_product_types'] = policy_product_types
        all_policies.append(res)

    return Response(all_policies, status.HTTP_200_OK)

# @swagger_auto_schema(
#     method='POST',
#     operation_description='Agent Claim Policy',
#     request_body=AgentClaimPolicySerializer,
#     responses={
#         200: 'OK',
#         400: 'Bad Request',
#         404: 'Not Found'
#     },
#     tags=['Agent']
# )
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def agent_claim_policy(request):
#     agent_id = request.user.id
#     serializer_class = AgentClaimPolicySerializer(data=request.data)
#
#     if not serializer_class.is_valid():
#         return Response({
#             serializer_class.errors
#         }, status.HTTP_400_BAD_REQUEST)
#
#     try:
#         policy_name = serializer_class.validated_data.get('policy_name')
#         quantity = serializer_class.validated_data.get('quantity_bought')
#
#         agent = Agent.objects.get(id=agent_id)
#         policy_obj = Policies.objects.get(name=policy_name)
#
#         """
#         Checks to see if the policy already exists in the AgentPolicy table.
#         ISSUE: Figure out how to renew a policy that has expired and how to buy the same
#         policy if the quantity_bought is 0.
#         """
#         if AgentPolicy.objects.filter(agent=agent, policy=policy_obj).exists():
#             return Response({
#                 "error": "You have claimed this policy already"
#             }, status.HTTP_400_BAD_REQUEST)
#
#         policy = AgentPolicy.objects.create(agent=agent, policy=policy_obj, quantity_bought=quantity)
#
#         policy.save()
#         return Response({
#             "message": "You have claimed a new policy"
#         }, status.HTTP_200_OK)
#
#     except Exception as e:
#         return Response({
#             "error": f"The error '{e}' occurred"
#         }, status.HTTP_400_BAD_REQUEST)
#

# @swagger_auto_schema(
#     method='GET',
#     operation_description='Agent Claim Policy',
#     responses={
#         200: 'OK',
#         400: 'Bad Request',
#         404: 'Not Found'
#     },
#     tags=['Agent']
# )
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def view_all_claimed_policies(request):
#     agent_id = request.user.id
#     agent = get_object_or_404(Agent, id=agent_id)
#     try:
#         queryset = AgentPolicy.objects.filter(agent=agent)
#         serializer_class = AgentViewAllClaimedPolicies(queryset, many=True)
#         return Response(serializer_class.data, status.HTTP_200_OK)
#
#     except Exception as e:
#         return Response({
#             "error": f"The error '{e}' occurred"
#         }, status.HTTP_400_BAD_REQUEST)
