from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.html import strip_tags
from django.template.loader import render_to_string

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from insurer.models import Insurer, InvitedAgents

from user.models import CustomUser

from superpool_proxy.superpool_client import SuperpoolClient

from .utils import generate_otp, generate_unyte_unique_agent_id
from .models import Agent
from .serializer import (
    CreateAgentSerializer,
    ShipmentAdditionalInformationSerializer,
    BikePolicyAdditionalInformationSerializer,
    MotorPolicyAdditionalInformationSerializer,
    DevicePolicyAdditionalInformationSerializer,
    TravelPolicyAdditionalInformationSerializer,
)
from .response_serializers import (
    SuccessfulCreateAgentSerializer,
)

SUPERPPOOL_HANDLER = SuperpoolClient()

@swagger_auto_schema(
    method='POST',
    manual_parameters=[
        openapi.Parameter('invite', openapi.IN_QUERY, description='Insurer unique unyte id', type=openapi.TYPE_STRING),
    ],
    request_body=CreateAgentSerializer,
    operation_description='Create New Agent',
    responses={
        '201': openapi.Response(
            'Created',
            SuccessfulCreateAgentSerializer,
        ),
        '400': 'Bad Request',
    },
    tags=['Agent'],
)
@api_view(['POST'])
def create_agent(request) -> Response:
    serializer_class = CreateAgentSerializer(data=request.data)

    if request.query_params.get('invite') is None:
        return Response({'error': "Can't find your Insurer's identifier"}, status.HTTP_400_BAD_REQUEST)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        user_email = serializer_class.validated_data.get('email')
        user_password = serializer_class.validated_data.get('password')

        uuid = request.query_params.get('invite')
        insurer = get_object_or_404(Insurer, unyte_unique_insurer_id=uuid)

        user_email = serializer_class.validated_data.get('email')
        user_password = serializer_class.validated_data.get('password')

        """
        Check to see if the agent who is attempting to register is under the list of invited agents.
        """
        insurer_invited_agents_objs = InvitedAgents.objects.filter(insurer=insurer).values()
        insurer_invited_agents = [email.get('agent_email') for email in insurer_invited_agents_objs]

        if user_email not in insurer_invited_agents:
            return Response({
                "error": "Unauthorized email. No Insurer has invited an agent with this email"
            }, status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.create_user(email=user_email, password=user_password, is_agent=True)
        user.save()

        agent_data = serializer_class.validated_data

        first_name = agent_data.get('first_name')
        last_name = agent_data.get('last_name')
        bank_account = agent_data.get('bank_account')
        middle_name = agent_data.get('middle_name')
        home_address = agent_data.get('home_address')
        bvn = agent_data.get('bvn')
        agent_data['affiliated_company'] = insurer

        uuad = generate_unyte_unique_agent_id(first_name, bank_account)

        agent = Agent.objects.create(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            home_address=home_address,
            bank_account=bank_account,
            bvn=bvn,
            affiliated_company=insurer,
            unyte_unique_agent_id=uuad,
            otp=generate_otp(),
            user=user,
            otp_created_at=timezone.now().time(),
        )
        agent.save()
        current_year = timezone.now().year

        context = {'current_year': current_year, 'name': f'{first_name} {last_name}'}
        html_message = render_to_string('agents/welcome.html', context=context)
        plain_html_message = strip_tags(html_message)

        send_mail(
            subject='Welcome email',
            message=plain_html_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.TO_EMAIL, user_email],
            html_message=html_message,
        )

        message = {'id': agent.id, 'message': f'Account successfully created for {first_name} {last_name}'}
        return Response(message, status=status.HTTP_201_CREATED)

    except Exception as e:
        message = {'error': e.__str__()}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='GET',
    operation_description='View Products From Insurer',
    responses={
        '200': 'OK',
        '400': 'Bad Request',
    },
    tags=['Agent'],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_products_for_insurer(request: Request):
    agent = get_object_or_404(Agent, pk=request.user.id)
    insurer = get_object_or_404(Insurer, pk=agent.affiliated_company)

    # TODO: Change insurer_id to added insurer UUID for proper fetching of insurer from DB after syncing with superpool
    response = SUPERPPOOL_HANDLER.get_all_products_for_one_insurer(insurer_id=insurer.id)
    status_code = response.get('status_code')
    error = response.get('error')
    data = response.get('data')

    if status_code != 200:
        return Response(error, status.HTTP_400_BAD_REQUEST)

    return Response(data, status.HTTP_200_OK)

@swagger_auto_schema(
    method='GET',
    operation_description='View Policies From Insurer',
    responses={
        '200': 'OK',
        '400': 'Bad Request',
    },
    tags=['Agent'],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_policies_for_insurer(request: Request):
    agent = get_object_or_404(Agent, pk=request.user.id)
    insurer = get_object_or_404(Insurer, pk=agent.affiliated_company)

    # TODO: Change insurer_id to added insurer UUID for proper fetching of insurer from DB after syncing with superpool
    response = SUPERPPOOL_HANDLER.get_all_policies_for_one_insurer(insurer_id=insurer.id)
    status_code = response.get('status_code')
    error = response.get('error')
    data = response.get('data')

    if status_code != 200:
        return Response(error, status.HTTP_400_BAD_REQUEST)

    return Response(data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='GET',
    operation_description='View Policies From Insurer',
    responses={
        '200': 'OK',
        '400': 'Bad Request',
    },
    tags=['Agent'],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_claims_for_insurer(request: Request):
    agent = get_object_or_404(Agent, pk=request.user.id)
    insurer = get_object_or_404(Insurer, pk=agent.affiliated_company)

    # TODO: Change insurer_id to added insurer UUID for proper fetching of insurer from DB after syncing with superpool
    response = SUPERPPOOL_HANDLER.get_all_claims_for_one_insurer(insurer_id=insurer.id)
    status_code = response.get('status_code')
    error = response.get('error')
    data = response.get('data')

    if status_code != 200:
        return Response(error, status.HTTP_400_BAD_REQUEST)

    return Response(data, status.HTTP_200_OK)


@swagger_auto_schema(
    methods=['POST'],
    operation_description='Travel Policy data needed to generate quotes',
    request_body=TravelPolicyAdditionalInformationSerializer,
    responses={
        '200': 'OK',
        '400': 'Bad Request',
    },
    tags=['Agent'],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def travel_policy(request: Request, product_name: str):
    agents = get_object_or_404(Agent, request.user.id)
    insurer = get_object_or_404(Insurer, agents.affiliated_company)
    insurer_business_name = insurer.business_name
    serializer_class = TravelPolicyAdditionalInformationSerializer(data=request.data)
    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)
    customer_metadata = serializer_class.validated_data.get('customer_metadata')
    insurance_details = serializer_class.validated_data.get('insurance_details')
    response = SUPERPPOOL_HANDLER.get_quote(customer_metadata, insurance_details, coverage_preferences={})
    quotes = response.get('data').get('data')
    product_quote = [company_quotes.get('provider') == insurer_business_name for company_quotes in quotes]
    result = None

    for product in product_quote:
        if product.get('product') == product_name and result is None:
            result = product

    return Response(result, status.HTTP_200_OK)


@swagger_auto_schema(
    methods=['GET'],
    operation_description='Device Policy data needed to generate quotes',
    responses={
        '200': 'OK',
        '400': 'Bad Request',
    },
    tags=['Agent'],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def device_policy(request: Request):
    serializer_class = DevicePolicyAdditionalInformationSerializer()
    return Response(serializer_class.data, status.HTTP_200_OK)


@swagger_auto_schema(
    methods=['GET'],
    operation_description='Motor Policy data needed to generate quotes',
    responses={
        '200': 'OK',
        '400': 'Bad Request',
    },
    tags=['Agent'],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def motor_policy(request: Request):
    serializer_class = MotorPolicyAdditionalInformationSerializer()
    return Response(serializer_class.validate, status.HTTP_200_OK)


@swagger_auto_schema(
    methods=['GET'],
    operation_description='Bike Policy data needed to generate quotes',
    responses={
        '200': 'OK',
        '400': 'Bad Request',
    },
    tags=['Agent'],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bike_policy(request: Request):
    serializer_class = BikePolicyAdditionalInformationSerializer()
    return Response(serializer_class.validate, status.HTTP_200_OK)


@swagger_auto_schema(
    methods=['GET'],
    operation_description='Shipment Policy data needed to generate quotes',
    responses={
        '200': 'OK',
        '400': 'Bad Request',
    },
    tags=['Agent'],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def shipment_policy(request: Request):
    serializer_class = ShipmentAdditionalInformationSerializer()
    return Response(serializer_class.validate, status.HTTP_200_OK)
