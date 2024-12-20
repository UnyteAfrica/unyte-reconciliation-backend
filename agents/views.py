from pprint import pprint

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

from .utils import add_string_to_all_fields_in_travel_serializer, generate_otp, create_merchant_on_superpool, generate_unyte_unique_agent_id
from .models import Agent
from .serializer import (
    BikePolicySerializer,
    CreateAgentSerializer,
    MotorPolicySerializer,
    GadgetPolicySerializer,
    SellMotorPolicySerializer,
    SellShipmentPolicySerializer,
    TravelPolicySerializer,
    ShipmentPolicySerializer,
    SellTravelPolicySerializer,
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
        first_name = serializer_class.validated_data.get('first_name')
        last_name = serializer_class.validated_data.get('last_name')
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

        data = {
            'company_name': f"{first_name} {last_name}",
            'business_email': user_email,
            'support_email': user_email
        }
        superpool_merchant = create_merchant_on_superpool(data)
        if superpool_merchant.get("status_code") != 201:
            return Response({
                'error': superpool_merchant.get('error')
            }, status=status.HTTP_400_BAD_REQUEST)
        user = CustomUser.objects.create_user(email=user_email, password=user_password, is_agent=True)
        user.save()

        agent_data = serializer_class.validated_data

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
            merchant_code = superpool_merchant.get('result').get('data').get('short_code'),
            tenant_id = superpool_merchant.get('result').get('data').get('tenant_id'),
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
    user = get_object_or_404(CustomUser, pk=request.user.id)
    agent = get_object_or_404(Agent, user=user)
    insurer = get_object_or_404(Insurer, pk=agent.affiliated_company_id)

    # TODO: Change insurer_id to added insurer UUID for proper fetching of insurer from DB after syncing with superpool
    response = SUPERPPOOL_HANDLER.get_all_products_for_one_insurer(insurer_id=insurer.insurer_id)
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
    user = get_object_or_404(CustomUser, pk=request.user.id)
    agent = get_object_or_404(Agent, user=user)
    insurer = get_object_or_404(Insurer, pk=agent.affiliated_company_id)

    # TODO: Change insurer_id to added insurer UUID for proper fetching of insurer from DB after syncing with superpool
    response = SUPERPPOOL_HANDLER.get_all_policies_for_one_insurer(insurer_id=insurer.insurer_id)
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
    user = get_object_or_404(CustomUser, pk=request.user.id)
    agent = get_object_or_404(Agent, user=user)
    agent = get_object_or_404(Agent, pk=request.user.id)
    insurer = get_object_or_404(Insurer, pk=agent.affiliated_company_id)

    # TODO: Change insurer_id to added insurer UUID for proper fetching of insurer from DB after syncing with superpool
    response = SUPERPPOOL_HANDLER.get_all_claims_for_one_insurer(insurer_id=insurer.insurer_id)
    status_code = response.get('status_code')
    error = response.get('error')
    data = response.get('data')

    if status_code != 200:
        return Response(error, status.HTTP_400_BAD_REQUEST)

    return Response(data, status.HTTP_200_OK)


@swagger_auto_schema(
    methods=['POST'],
    operation_description='Travel Policy data needed to generate quotes',
    request_body=TravelPolicySerializer,
    responses={
        '200': 'OK',
        '400': 'Bad Request',
    },
    tags=['Agent'],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_travel_quotes(request: Request, product_name: str):
    user = get_object_or_404(CustomUser, pk=request.user.id)
    agents = get_object_or_404(Agent, user=user.id)
    insurer = get_object_or_404(Insurer, pk=agents.affiliated_company_id)
    insurer_business_name = insurer.business_name
    serializer_class = TravelPolicySerializer(data=request.data)
    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)
    customer_metadata = serializer_class.validated_data.get('customer_metadata')
    insurance_details = serializer_class.validated_data.get('insurance_details')
    response = SUPERPPOOL_HANDLER.get_quote(customer_metadata, insurance_details, coverage_preferences={})
    status_code = response.get('status_code')

    if status_code != 200:
        return Response(response.get('error'), status.HTTP_400_BAD_REQUEST)

    quotes = response.get('data').get('data')
    insurer_quotes = []
    result = []
    for product in quotes:
        if insurer_business_name == product.get('provider'):
            insurer_quotes.append(product)  # noqa: PERF401

    for policy in insurer_quotes:
        if policy.get('product') == product_name:
            result.append(policy)  # noqa: PERF401

    return Response({"data": result[0]}, status.HTTP_200_OK)


@swagger_auto_schema(
    methods=['POST'],
    operation_description='Motor Policy data needed to generate quotes',
    request_body=MotorPolicySerializer(),
    responses={
        '200': 'OK',
        '400': 'Bad Request',
    },
    tags=['Agent'],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_motor_quotes(request: Request, product_name: str):
    user = get_object_or_404(CustomUser, pk=request.user.id)
    agents = get_object_or_404(Agent, user=user.id)
    insurer = get_object_or_404(Insurer, pk=agents.affiliated_company_id)
    insurer_business_name = insurer.business_name
    serializer_class = MotorPolicySerializer(data=request.data)
    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)
    customer_metadata = serializer_class.validated_data.get('customer_metadata')
    insurance_details = serializer_class.validated_data.get('insurance_details')
    response = SUPERPPOOL_HANDLER.get_quote(customer_metadata, insurance_details, coverage_preferences={})
    status_code = response.get('status_code')

    if status_code != 200:
        return Response(response.get('error'), status.HTTP_400_BAD_REQUEST)

    quotes = response.get('data').get('data')
    insurer_quotes = []
    result = []

    for product in quotes:
        if insurer_business_name == product.get('provider'):
            insurer_quotes.append(product)  # noqa: PERF401

    for policy in insurer_quotes:
        if policy.get('product') == product_name:
            result.append(policy)  # noqa: PERF401

    return Response({"data": result}, status.HTTP_200_OK)



@swagger_auto_schema(
    methods=['POST'],
    operation_description='Gadget Policy data needed to generate quotes',
    request_body=GadgetPolicySerializer(),
    responses={
        '200': 'OK',
        '400': 'Bad Request',
    },
    tags=['Agent'],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_gadget_quotes(request: Request, product_name: str):
    user = get_object_or_404(CustomUser, pk=request.user.id)
    agents = get_object_or_404(Agent, user=user.id)
    insurer = get_object_or_404(Insurer, pk=agents.affiliated_company_id)
    insurer_business_name = insurer.business_name
    serializer_class = GadgetPolicySerializer(data=request.data)
    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)
    customer_metadata = serializer_class.validated_data.get('customer_metadata')
    insurance_details = serializer_class.validated_data.get('insurance_details')
    response = SUPERPPOOL_HANDLER.get_quote(customer_metadata, insurance_details, coverage_preferences={})
    status_code = response.get('status_code')

    if status_code != 200:
        return Response(response.get('error'), status.HTTP_400_BAD_REQUEST)

    quotes = response.get('data').get('data')
    insurer_quotes = []
    result = []
    for product in quotes:
        if insurer_business_name == product.get('provider'):
            insurer_quotes.append(product)  # noqa: PERF401

    for policy in insurer_quotes:
        if policy.get('product') == product_name:
            result.append(policy)  # noqa: PERF401

    return Response({"data": result[0]}, status.HTTP_200_OK)


@swagger_auto_schema(
    methods=['POST'],
    operation_description='Bike Policy data needed to generate quotes',
    request_body=BikePolicySerializer(),
    responses={
        '200': 'OK',
        '400': 'Bad Request',
    },
    tags=['Agent'],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_bike_quotes(request: Request, product_name: str):
    user = get_object_or_404(CustomUser, pk=request.user.id)
    agents = get_object_or_404(Agent, user=user.id)
    insurer = get_object_or_404(Insurer, pk=agents.affiliated_company_id)
    insurer_business_name = insurer.business_name
    serializer_class = BikePolicySerializer(data=request.data)
    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)
    customer_metadata = serializer_class.validated_data.get('customer_metadata')
    insurance_details = serializer_class.validated_data.get('insurance_details')
    response = SUPERPPOOL_HANDLER.get_quote(customer_metadata, insurance_details, coverage_preferences={})
    status_code = response.get('status_code')

    if status_code != 200:
        return Response(response.get('error'), status.HTTP_400_BAD_REQUEST)

    quotes = response.get('data').get('data')
    insurer_quotes = []
    result = []
    for product in quotes:
        if insurer_business_name == product.get('provider'):
            insurer_quotes.append(product)  # noqa: PERF401

    for policy in insurer_quotes:
        if policy.get('product') == product_name:
            result.append(policy)  # noqa: PERF401

    return Response({"data": result}, status.HTTP_200_OK)



@swagger_auto_schema(
    methods=['POST'],
    operation_description='Shipment Policy data needed to generate quotes',
    request_body=ShipmentPolicySerializer(),
    responses={
        '200': 'OK',
        '400': 'Bad Request',
    },
    tags=['Agent'],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_shipment_quotes(request: Request, product_name: str):
    user = get_object_or_404(CustomUser, pk=request.user.id)
    agents = get_object_or_404(Agent, user=user.id)
    insurer = get_object_or_404(Insurer, pk=agents.affiliated_company_id)
    insurer_business_name = insurer.business_name
    serializer_class = ShipmentPolicySerializer(data=request.data)
    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)
    customer_metadata = serializer_class.validated_data.get('customer_metadata')
    insurance_details = serializer_class.validated_data.get('insurance_details')
    response = SUPERPPOOL_HANDLER.get_quote(customer_metadata, insurance_details, coverage_preferences={})
    status_code = response.get('status_code')

    if status_code != 200:
        return Response(response.get('error'), status.HTTP_400_BAD_REQUEST)

    quotes = response.get('data').get('data')
    insurer_quotes = []
    result = []
    for product in quotes:
        if insurer_business_name == product.get('provider'):
            insurer_quotes.append(product)  # noqa: PERF401

    for policy in insurer_quotes:
        if policy.get('product') == product_name:
            result.append(policy)  # noqa: PERF401

    return Response({"data": result}, status.HTTP_200_OK)


@swagger_auto_schema(
    methods=['POST'],
    operation_description='Sell Travel Policy',
    request_body=SellTravelPolicySerializer,
    responses={
        '200': 'OK',
        '400': 'Bad Request',
    },
    tags=['Agent'],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sell_travel_policy(request: Request):
    user = get_object_or_404(CustomUser, pk=request.user.id)
    agent = get_object_or_404(Agent, user=user)
    serializer_class = SellTravelPolicySerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)
    data = serializer_class.validated_data
    customer_metadata = data.get('customer_metadata')
    additional_information = data.get('additional_information')
    activation_metadata = data.get('activation_metadata')
    quote_code = data.get('quote_code')
    product_type = data.get('product_type')

    response = SUPERPPOOL_HANDLER.sell_policy(
        customer_metadata=customer_metadata,
        additional_information=additional_information,
        quote_code=quote_code,
        product_type=product_type,
        merchant_code=agent.merchant_code,
        activation_metadata=activation_metadata
    )
    if response.get('status_code') != 201:
        return Response({
            "error": response.get('error')
        }, status.HTTP_400_BAD_REQUEST)

    return Response({
        "message": response.get('data')
    }, status.HTTP_201_CREATED)



@swagger_auto_schema(
    methods=['POST'],
    operation_description='Sell Shipment Policy',
    request_body=SellShipmentPolicySerializer,
    responses={
        '200': 'OK',
        '400': 'Bad Request',
    },
    tags=['Agent'],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sell_shipment_policy(request: Request):
    user = get_object_or_404(CustomUser, pk=request.user.id)
    agent = get_object_or_404(Agent, user=user)
    serializer_class = SellShipmentPolicySerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)
    data = serializer_class.validated_data
    customer_metadata = data.get('customer_metadata')
    additional_information = data.get('additional_information')
    activation_metadata = data.get('activation_metadata')
    quote_code = data.get('quote_code')
    product_type = data.get('product_type')

    response = SUPERPPOOL_HANDLER.sell_policy(
        customer_metadata=customer_metadata,
        additional_information=additional_information,
        quote_code=quote_code,
        product_type=product_type,
        merchant_code=agent.merchant_code,
        activation_metadata=activation_metadata
    )
    if response.get('status_code') != 201:
        return Response({
            "error": response.get('error')
        }, status.HTTP_400_BAD_REQUEST)

    return Response({
        "message": response.get('data')
    }, status.HTTP_201_CREATED)




@swagger_auto_schema(
    methods=['POST'],
    operation_description='Sell Motor Policy',
    request_body=SellMotorPolicySerializer,
    responses={
        '200': 'OK',
        '400': 'Bad Request',
    },
    tags=['Agent'],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sell_motor_policy(request: Request):
    user = get_object_or_404(CustomUser, pk=request.user.id)
    agent = get_object_or_404(Agent, user=user)
    serializer_class = SellMotorPolicySerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)
    data = serializer_class.validated_data
    customer_metadata = data.get('customer_metadata')
    additional_information = data.get('additional_information')
    activation_metadata = data.get('activation_metadata')
    quote_code = data.get('quote_code')
    product_type = data.get('product_type')

    response = SUPERPPOOL_HANDLER.sell_policy(
        customer_metadata=customer_metadata,
        additional_information=additional_information,
        quote_code=quote_code,
        product_type=product_type,
        merchant_code=agent.merchant_code,
        activation_metadata=activation_metadata
    )
    if response.get('status_code') != 201:
        return Response({
            "error": response.get('error')
        }, status.HTTP_400_BAD_REQUEST)

    return Response({
        "message": response.get('data')
    }, status.HTTP_201_CREATED)


@swagger_auto_schema(
    methods=['GET'],
    operation_description='Travel Policy data needed to generate quotes',
    responses={
        '200': 'OK',
        '400': 'Bad Request',
    },
    tags=['Agent'],
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_travel_quote_response(request: Request):
    serializer_class = TravelPolicySerializer()
    add_string_to_all_fields_in_travel_serializer(serializer_class.data)
    return Response(serializer_class.data, status.HTTP_200_OK)

@swagger_auto_schema(
    methods=['GET'],
    operation_description='Gadget Policy data needed to generate quotes',
    responses={
        '200': 'OK',
        '400': 'Bad Request',
    },
    tags=['Agent'],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_gadget_quote_response(request: Request):
    serializer_class = GadgetPolicySerializer()
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
def get_motor_quote_response(request: Request):
    serializer_class = MotorPolicySerializer()
    return Response(serializer_class.data, status.HTTP_200_OK)


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
def get_bike_quote_response(request: Request):
    serializer_class = BikePolicySerializer()
    return Response(serializer_class.data, status.HTTP_200_OK)


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
def get_shipment_quote_response(request: Request):
    serializer_class = ShipmentPolicySerializer()
    return Response(serializer_class.data, status.HTTP_200_OK)


