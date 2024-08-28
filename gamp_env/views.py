from pprint import pprint

from django.shortcuts import get_object_or_404
from .serializers import GampUserSerializer, GampArbitraryPolicySerializer, GampArbitratyProductSerializer, \
    UserPolicySerializer, ViewUserPolicySerializer
from .models import GampArbitraryUser, GampArbitraryPolicy, GampArbitraryProduct, Product, ProductType, UserPolicy
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
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


# @swagger_auto_schema(
#     method='GET',
#     operation_description='Create Gamp Insurer Policies',
#     responses={
#         '201': "Created",
#         '400': 'Bad Request'
#     },
#     tags=['Gamp']
# )
# @api_view(['GET'])
# def view_policies(request: Request, policy_uuid: uuid4) -> Response:
#     try:
#         policy = GampArbitraryPolicy.objects.get(policy_uuid=policy_uuid)
#         all_products_per_policy = GampPolicyProducts.objects.filter(policy=policy)
#         print(all_products_per_policy)
#         # serializer_class = ViewAritraryPolicySerializer(all_products_per_policy, many=True)
#
#         # ChatGPT generated code
#         response_data = {
#             "product_name": policy.policy_name,
#             "insurer": policy.insurer,
#             "product_types": []
#         }
#
#         # Add the product details to the response
#         for product in all_products_per_policy:
#             response_data["product_types"].append({
#                 "type": product.policy.policy_type,
#                 "premium": product.product.premium,
#                 "flat_fee": product.product.flat_fee,
#                 "broker_commission": "20%"
#             })
#         return Response(response_data, status.HTTP_200_OK)
#
#     except Exception as e:
#         return Response({
#             "error": f"The error {e} occurred"
#         }, status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='GET',
    operation_description='View all Insurer policies with their product types',
    responses={
        '201': "Created",
        '400': 'Bad Request'
    },
    tags=['Gamp']
)
@api_view(['GET'])
def view_product_by_insurer(request, insurer: str):
    insurer = 'NEM'
    try:
        all_products = Product.objects.filter(insurer=insurer)
        hol = []

        for products in all_products:
            res = {'insurer': insurer, 'product_name': products.product_name}
            product_type_list = []

            product_types = ProductType.objects.filter(product=products)

            for product_type in product_types:
                product_type_list.append({
                    "name": product_type.type,
                    "premium": product_type.premium,
                    "flat_fee": product_type.flat_fee,
                    "broker_commission": product_type.broker_commission
                })
            res['product_type'] = product_type_list
            hol.append(res)
        return Response(hol, status.HTTP_200_OK)

    except Exception as e:
        return Response(e, status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    operation_description='Buy products by customers',
    request_body=UserPolicySerializer,
    responses={
        '201': "Created",
        '400': 'Bad Request'
    },
    tags=['Gamp']
)
@api_view(['POST'])
def customer_purchase_policy(request) -> Response:
    serializer_class = UserPolicySerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)
    first_name = serializer_class.validated_data.get('first_name')
    last_name = serializer_class.validated_data.get('last_name')
    product = serializer_class.validated_data.get('policy')
    product_types = serializer_class.validated_data.get('product_type')

    customer_obj = get_object_or_404(GampArbitraryUser, first_name=first_name, last_name=last_name)
    product_obj = get_object_or_404(Product, product_name=product)

    product_type_objs = ProductType.objects.filter(product=product_obj)

    product_type_list_obj = []

    for product_type_obj in product_type_objs:
        product_type_list_obj.append({
            "product_name": product_type_obj.type,
            "premium": product_type_obj.premium,
            "flat_fee": product_type_obj.flat_fee
        })

    for product_type in product_types:
        if product_type not in product_type_list_obj:
            print(product_type)
            continue
        else:
            print("I am here")
            try:
                policy_product_type = ProductType.objects.get(product=product_obj,
                                                              type=product_type.get('product_name'))
                customer_policy_obj = UserPolicy.objects.create(
                    customer=customer_obj,
                    product_bought=policy_product_type
                )
            except Exception as e:
                return Response({
                    "error": f"{e}"
                }, status.HTTP_200_OK)

    return Response({
        "message": "All available policies have been bought"
    }, status.HTTP_200_OK)


@swagger_auto_schema(
    method='POST',
    operation_description='Buy products by customers',
    request_body=ViewUserPolicySerializer,
    responses={
        '201': "Created",
        '400': 'Bad Request'
    },
    tags=['Gamp']
)
@api_view(['POST'])
def view_policies_customer_bought(request) -> Response:
    serializer_class = ViewUserPolicySerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)

    first_name = serializer_class.validated_data.get("first_name")
    last_name = serializer_class.validated_data.get("last_name")
    customer_obj = get_object_or_404(GampArbitraryUser, first_name=first_name, last_name=last_name)

    try:
        user_policy_obj = UserPolicy.objects.filter(customer=customer_obj)
        res = {'customer': f"{customer_obj.first_name} {customer_obj.last_name}"}
        # bought_policies = []
        bought_policies = {}
        val = {}

        for user_policy in user_policy_obj:
            policy_name = user_policy.product_bought.product.product_name

            # Check if the policy already exists in the dictionary
            if policy_name not in bought_policies:
                bought_policies[policy_name] = {
                    "policy": policy_name,
                    "product(s)": []
                }

            # Append the product details to the corresponding policy's product list
            bought_policies[policy_name]["product(s)"].append({
                "product_name": user_policy.product_bought.type,
                "premium": user_policy.product_bought.premium,
                "flat_fee": user_policy.product_bought.flat_fee,
            })

        # Convert the dictionary back to a list
        bought_policies_list = list(bought_policies.values())
        res['policies_purchased'] = bought_policies_list


        """
        NOT FUNCTIONAL
        """
        # for user_policy in user_policy_obj:
        #     # policy = user_policy.product_bought.product.product_name
        #     # print(user_policy)
        #     if user_policy in user_policy_obj:
        #         print(user_policy)
        #     bought_policies.append({
        #         "policy": user_policy.product_bought.product.product_name,
        #         "product(s)": [
        #             {
        #                 "product_name": user_policy.product_bought.type,
        #                 "premium": user_policy.product_bought.premium,
        #                 "flat_fee": user_policy.product_bought.flat_fee,
        #             }
        #         ]
        #         # "product_name": user_policy.product_bought.type,
        #         # "premium": user_policy.product_bought.premium,
        #         # "flat_fee": user_policy.product_bought.flat_fee,
        #     })
        # res['policies_purchased'] = bought_policies

        return Response(res, status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "error": f"{e}"
        }, status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def view_claims_made_by_customer(customer: str):
    pass


@api_view(['GET'])
def view_all_devices_insured_by_customer(customer: str):
    pass


@api_view(['GET'])
def view_all_devices_insured_by_a_policy():
    pass
