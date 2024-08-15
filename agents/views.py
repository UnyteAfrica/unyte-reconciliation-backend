from datetime import datetime

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
from policies.models import Policies, AgentPolicy
from .models import Agent, AgentProfile
from .serializer import CreateAgentSerializer, LoginAgentSerializer, AgentSendNewOTPSerializer, AgentOTPSerializer, \
    AgentForgotPasswordEmailSerializer, AgentForgotPasswordResetSerializer, ViewAgentDetailsSerializer, \
    UpdateAgentDetails, AgentClaimPolicySerializer, AgentSellPolicySerializer, AgentViewAllClaimedPolicies, \
    ViewAgentProfile, LogoutAgentSerializer, AgentValidateRefreshToken, AgentViewAllAvailablePolicies
from .utils import generate_otp, verify_otp, gen_absolute_url, generate_unyte_unique_agent_id


@swagger_auto_schema(
    method='POST',
    manual_parameters=[
        openapi.Parameter('invite',
                          openapi.IN_QUERY,
                          description="Insurer unyte id",
                          type=openapi.TYPE_STRING),
    ],
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
    operation_description='Login Agent',
    request_body=LogoutAgentSerializer,
    responses={
        '200': "OK",
        '400': 'Bad Request'
    },
    tags=['Agent']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_agent(request):
    serializer_class = LogoutAgentSerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)

    serializer_class.save()

    return Response({
        "message": "Agent successfully logged out"
    }, status.HTTP_200_OK)


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
        message = {
            'message': 'OTP Verified'
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
    method='POST',
    operation_description='Refresh Access Token',
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
def update_agent_details(request):
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


@swagger_auto_schema(
    method='POST',
    operation_description='Agent Claim Policy',
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
def agent_sell_policy(request):
    agent_id = request.user.id
    serializer_class = AgentSellPolicySerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response({
            serializer_class.errors
        }, status.HTTP_400_BAD_REQUEST)

    policy_name = serializer_class.validated_data.get('policy_name')
    policy_obj = get_object_or_404(Policies, name=policy_name)

    agent = get_object_or_404(Agent, pk=agent_id)
    policy = get_object_or_404(AgentPolicy, agent=agent, policy=policy_obj)

    quantity_to_sell = serializer_class.validated_data.get('quantity_to_sell')

    """
    Check if the policy is_sold value is set to True and the quantity_bought is zero
    """
    if policy.is_sold and (policy.quantity_bought == 0):
        return Response({
            "error": "You cannot sell this policy anymore. "
                     "Reach out to your insurer to request for more"
        }, status.HTTP_400_BAD_REQUEST)

    """
    Check if the policy can be sold
    """
    if not policy.can_sell_policy(policy_obj):
        return Response({
            "error": "You cannot sell this policy, it's invalid"
        }, status.HTTP_400_BAD_REQUEST)

    if quantity_to_sell > policy.quantity_bought:
        return Response({
            "error": "You cannot sell above your current policy quantity"
        }, status.HTTP_400_BAD_REQUEST)

    policy.is_sold = True
    policy.quantity_bought = policy.quantity_bought - quantity_to_sell
    policy.quantity_sold = policy.quantity_sold + quantity_to_sell
    policy.save()

    return Response({
        "message": "You have successfully sold this policy"
    }, status.HTTP_200_OK)

@swagger_auto_schema(
    method='POST',
    operation_description='Agent Claim Policy',
    request_body=AgentClaimPolicySerializer,
    responses={
        200: 'OK',
        400: 'Bad Request',
        404: 'Not Found'
    },
    tags=['Agent']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def agent_claim_policy(request):
    agent_id = request.user.id
    serializer_class = AgentClaimPolicySerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response({
            serializer_class.errors
        }, status.HTTP_400_BAD_REQUEST)

    try:
        policy_name = serializer_class.validated_data.get('policy_name')
        quantity = serializer_class.validated_data.get('quantity_bought')

        agent = Agent.objects.get(id=agent_id)
        policy_obj = Policies.objects.get(name=policy_name)

        """
        Checks to see if the policy already exists in the AgentPolicy table.
        ISSUE: Figure out how to renew a policy that has expired and how to buy the same 
        policy if the quantity_bought is 0.
        """
        if AgentPolicy.objects.filter(agent=agent, policy=policy_obj).exists():
            return Response({
                "error": "You have claimed this policy already"
            }, status.HTTP_400_BAD_REQUEST)

        policy = AgentPolicy.objects.create(agent=agent, policy=policy_obj, quantity_bought=quantity)

        policy.save()
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
    tags=['Agent']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_claimed_policies(request):
    agent_id = request.user.id
    agent = get_object_or_404(Agent, id=agent_id)
    try:
        queryset = AgentPolicy.objects.filter(agent=agent)
        serializer_class = AgentViewAllClaimedPolicies(queryset, many=True)
        return Response(serializer_class.data, status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "error": f"The error '{e}' occurred"
        }, status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='GET',
    operation_description='Sold Policies',
    responses={
        200: 'OK',
        400: 'Bad Request',
        404: 'Not Found'
    },
    tags=['Agent']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_sold_policies(request):
    agent_id = request.user.id
    agent = get_object_or_404(Agent, id=agent_id)
    queryset = AgentPolicy.objects.filter(agent=agent, is_sold=True)
    serializer_class = AgentViewAllClaimedPolicies(queryset, many=True)

    return Response(serializer_class.data, status.HTTP_200_OK)


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
    operation_description='View All Available Policies',
    responses={
        200: 'OK',
        400: 'Bad Request',
        404: 'Not Found'
    },
    tags=['Agent']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_available_policies(request) -> Response:
    agent_id = request.user.id
    agent = get_object_or_404(Agent, pk=agent_id)
    insurer = agent.affiliated_company

    try:
        policies_queryset = Policies.objects.filter(insurer=insurer)
        serializer_class = AgentViewAllAvailablePolicies(policies_queryset, many=True)

        return Response(serializer_class.data, status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "error": f"The error '{e}' occurred"
        })
