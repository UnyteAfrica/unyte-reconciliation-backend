from uuid import uuid4

from django.shortcuts import render
from .serializers import GampUserSerializer, GampDeviceSerializer, GampClaimSerializer, GampArbitraryPolicySerializer, \
    GampArbitratyProductSerializer, ViewAritraryPolicySerializer, GampPolicyProducts
from .models import GampArbitraryUser, GampArbitraryPolicy, GampArbitraryProduct
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from faker import Faker
import random


@swagger_auto_schema(
    method='GET',
    operation_description='Create Gamp User(s)',
    responses={
        '201': "Created",
        '400': 'Bad Request'
    },
    tags=['Gamp']
)
@api_view(['GET'])
def create_gamp_users(request: Request, count: int) -> Response:
    fake = Faker()

    for _ in range(count):
        GampArbitraryUser.objects.create(
            uuid=fake.uuid4(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone_number=fake.phone_number(),
            email=fake.email()
        )
    try:
        all_users = GampArbitraryUser.objects.all()
        queryset = GampUserSerializer(all_users, many=True)
        return Response(queryset.data, status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "error": f"The error '{e}' occurred"
        })


@swagger_auto_schema(
    method='GET',
    operation_description='Create Gamp Policies',
    responses={
        '201': "Created",
        '400': 'Bad Request'
    },
    tags=['Gamp']
)
@api_view(['GET'])
def create_policy_with_insurer(request: Request, count: int, insurer: str) -> Response:
    fake = Faker()
    policy_names = [
        "Smart Motorist Protection Plan",
        "Smart Traveler Protection Plan",
        "Smart Generations Protection",
        "Home Protection Policy",
        "Personal Accident",
        "Student Protection Plan",
        "Auto Insurance"
    ]
    policy_types = [
        "Launch",
        "Credit Life",
        "Device Protection",
        "Travel Cover",
        "Health",
        "Motor Registration / Insurance",
        "Student Protection",
        "Logistics / GIT",
        "Card Protection"
    ]
    description = [
        "New description",
        "A new description has arrived",
        "Description of new"
    ]

    try:
        for _ in range(count):
            GampArbitraryPolicy.objects.create(
                policy_uuid=fake.uuid4(),
                policy_name=random.choice(policy_names),
                policy_type=random.choice(policy_types),
                description=random.choice(description),
                insurer=insurer
            )

        all_policies = GampArbitraryPolicy.objects.all()
        queryset = GampArbitraryPolicySerializer(all_policies, many=True)
        return Response(queryset.data, status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "error": f"The error '{e}' occurred"
        })


@swagger_auto_schema(
    method='GET',
    operation_description='Create Gamp Products',
    responses={
        '201': "Created",
        '400': 'Bad Request'
    },
    tags=['Gamp']
)
@api_view(['GET'])
def create_products_for_policy(request: Request, count: int) -> Response:
    fake = Faker()
    product_names = [
        "Basic",
        "Standard",
        "Premium"
    ]
    try:

        for _ in range(count):
            GampArbitraryProduct.objects.create(
                product_uuid=fake.uuid4(),
                product_name=random.choice(product_names),
                flat_fee=fake.boolean(),
                premium=fake.pricetag()
            )

        all_products = GampArbitraryProduct.objects.all()
        queryset = GampArbitratyProductSerializer(all_products, many=True)
        return Response(queryset.data, status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "error": f"The error '{e}' occurred"
        })


@swagger_auto_schema(
    method='GET',
    operation_description='Create Gamp Insurer Policies',
    responses={
        '201': "Created",
        '400': 'Bad Request'
    },
    tags=['Gamp']
)
@api_view(['GET'])
def view_policies(request: Request, policy_uuid: uuid4) -> Response:
    try:
        policy = GampArbitraryPolicy.objects.get(policy_uuid=policy_uuid)
        all_products_per_policy = GampPolicyProducts.objects.filter(policy=policy)
        print(all_products_per_policy)
        # serializer_class = ViewAritraryPolicySerializer(all_products_per_policy, many=True)

        # ChatGPT generated code
        response_data = {
            "product_name": policy.policy_name,
            "insurer": policy.insurer,
            "product_types": []
        }

        # Add the product details to the response
        for product in all_products_per_policy:
            response_data["product_types"].append({
                "type": product.policy.policy_type,
                "premium": product.product.premium,
                "flat_fee": product.product.flat_fee,
                "broker_commission": "20%"
            })
        return Response(response_data, status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "error": f"The error {e} occurred"
        }, status.HTTP_400_BAD_REQUEST)
