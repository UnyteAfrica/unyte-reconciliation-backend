import uuid

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from user.models import CustomUser

from .superpool_client import SuperpoolClient

SUPERPOOL_HANDLER = SuperpoolClient()
SUPERPOOL_PROXY_TAG = 'Dashboard'


@swagger_auto_schema(
    method='GET',
    operation_description='Get all products from Superpool',
    responses={200: openapi.Response('OK'), 400: 'Bad Request'},
    tags=[SUPERPOOL_PROXY_TAG],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_products(request: Request) -> Response:
    user = get_object_or_404(CustomUser, pk=request.user.id)
    if user.is_agent:
        return Response({
            'error': 'Agents cannot view all products'
        }, status.HTTP_400_BAD_REQUEST)
    response = SUPERPOOL_HANDLER.get_all_products()
    status_code = response.get('status_code')
    error = response.get('error')
    data = response.get('data')

    if status_code != 200:
        return Response(error, status.HTTP_400_BAD_REQUEST)

    return Response(data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='GET',
    operation_description='Get all products for one merchant Superpool',
    responses={200: openapi.Response('OK'), 400: 'Bad Request'},
    tags=[SUPERPOOL_PROXY_TAG],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_products_one_merchant(request: Request, merchant_id: uuid) -> Response:
    user = get_object_or_404(CustomUser, pk=request.user.id)
    if user.is_agent or user.is_insurer:
        return Response({
            'error': 'Unathorized entity access'
        }, status.HTTP_403_FORBIDDEN)
    response = SUPERPOOL_HANDLER.get_all_products_one_merchant(merchant_id)
    status_code = response.get('status_code')
    error = response.get('error')
    data = response.get('data')

    if status_code != 200:
        return Response(error, status.HTTP_400_BAD_REQUEST)

    return Response(data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='GET',
    operation_description='Get all policies for one merchant from Superpool',
    responses={200: openapi.Response('OK'), 400: 'Bad Request'},
    tags=[SUPERPOOL_PROXY_TAG],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_policies_one_merchant(request: Request, merchant_id: uuid) -> Response:
    user = get_object_or_404(CustomUser, pk=request.user.id)
    if user.is_agent or user.is_insurer:
        return Response({
            'error': 'Unathorized entity access'
        }, status.HTTP_403_FORBIDDEN)
    response = SUPERPOOL_HANDLER.get_all_policies_one_merchant(merchant_id)
    status_code = response.get('status_code')
    error = response.get('error')
    data = response.get('data')

    if status_code != 200:
        return Response(error, status.HTTP_400_BAD_REQUEST)

    return Response(data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='GET',
    operation_description='Get all claims for one merchant from Superpool',
    responses={200: openapi.Response('OK'), 400: 'Bad Request'},
    tags=[SUPERPOOL_PROXY_TAG],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_claims_one_merchant(request: Request, merchant_id: uuid) -> Response:
    user = get_object_or_404(CustomUser, pk=request.user.id)
    if user.is_agent or user.is_insurer:
        return Response({
            'error': 'Unathorized entity access'
        }, status.HTTP_403_FORBIDDEN)
    response = SUPERPOOL_HANDLER.get_all_claims_one_merchant(merchant_id)
    status_code = response.get('status_code')
    error = response.get('error')
    data = response.get('data')

    if status_code != 200:
        return Response(error, status.HTTP_400_BAD_REQUEST)

    return Response(data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='GET',
    operation_description='Get all products for one insurer from Superpool',
    responses={200: openapi.Response('OK'), 400: 'Bad Request'},
    tags=[SUPERPOOL_PROXY_TAG],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_products_one_insurer(request: Request, insurer_id: uuid) -> Response:
    user = get_object_or_404(CustomUser, pk=request.user.id)
    if user.is_agent or user.is_merchant:
        return Response({
            'error': 'Unathorized entity access'
        }, status.HTTP_403_FORBIDDEN)
    response = SUPERPOOL_HANDLER.get_all_products_one_insurer(insurer_id)
    status_code = response.get('status_code')
    error = response.get('error')
    data = response.get('data')

    if status_code != 200:
        return Response(error, status.HTTP_400_BAD_REQUEST)

    return Response(data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='GET',
    operation_description='Get all policies for one insurer from Superpool',
    responses={200: openapi.Response('OK'), 400: 'Bad Request'},
    tags=[SUPERPOOL_PROXY_TAG],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_policies_one_insurer(request: Request, insurer_id: uuid) -> Response:
    user = get_object_or_404(CustomUser, pk=request.user.id)
    if user.is_agent or user.is_merchant:
        return Response({
            'error': 'Unathorized entity access'
        }, status.HTTP_403_FORBIDDEN)
    response = SUPERPOOL_HANDLER.get_all_policies_one_insurer(insurer_id)
    status_code = response.get('status_code')
    error = response.get('error')
    data = response.get('data')

    if status_code != 200:
        return Response(error, status.HTTP_400_BAD_REQUEST)

    return Response(data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='GET',
    operation_description='Get all claims for one insurer from Superpool',
    responses={200: openapi.Response('OK'), 400: 'Bad Request'},
    tags=[SUPERPOOL_PROXY_TAG],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_claims_one_insurer(request: Request, insurer_id: uuid) -> Response:
    user = get_object_or_404(CustomUser, pk=request.user.id)
    if user.is_agent or user.is_merchant:
        return Response({
            'error': 'Unathorized entity access'
        }, status.HTTP_403_FORBIDDEN)
    response = SUPERPOOL_HANDLER.get_all_claims_one_insurer(insurer_id)
    status_code = response.get('status_code')
    error = response.get('error')
    data = response.get('data')

    if status_code != 200:
        return Response(error, status.HTTP_400_BAD_REQUEST)

    return Response(data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='GET',
    operation_description='Get all product_types sold by agents for one insurer from Superpool',
    responses={200: openapi.Response('OK'), 400: 'Bad Request'},
    tags=[SUPERPOOL_PROXY_TAG],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_product_types_sold_by_agent_for_one_insurer(request: Request, insurer_id: uuid) -> Response:
    user = get_object_or_404(CustomUser, pk=request.user.id)
    if user.is_agent or user.is_merchant:
        return Response({
            'error': 'Unathorized entity access'
        }, status.HTTP_403_FORBIDDEN)
    response = SUPERPOOL_HANDLER.get_all_product_types_sold_by_agent_for_one_insurer(insurer_id)
    status_code = response.get('status_code')
    error = response.get('error')
    data = response.get('data')

    if status_code != 200:
        return Response(error, status.HTTP_400_BAD_REQUEST)

    return Response(data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='GET',
    operation_description='Get all customers agents product_types for one insurer from Superpool',
    responses={200: openapi.Response('OK'), 400: 'Bad Request'},
    tags=[SUPERPOOL_PROXY_TAG],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_customers_agent_sold_product_types_for_one_insurer(request: Request, insurer_id: uuid) -> Response:
    user = get_object_or_404(CustomUser, pk=request.user.id)
    if user.is_agent or user.is_merchant:
        return Response({
            'error': 'Unathorized entity access'
        }, status.HTTP_403_FORBIDDEN)
    response = SUPERPOOL_HANDLER.get_all_customers_agent_sold_product_types_for_one_insurer(insurer_id)
    status_code = response.get('status_code')
    error = response.get('error')
    data = response.get('data')

    if status_code != 200:
        return Response(error, status.HTTP_400_BAD_REQUEST)

    return Response(data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='GET',
    operation_description='Get all products for one insurer from Superpool',
    responses={200: openapi.Response('OK'), 400: 'Bad Request'},
    tags=[SUPERPOOL_PROXY_TAG],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_product_sold_by_agent_for_one_insurer(request: Request, insurer_id: uuid) -> Response:
    user = get_object_or_404(CustomUser, pk=request.user.id)
    if user.is_agent or user.is_merchant:
        return Response({
            'error': 'Unathorized entity access'
        }, status.HTTP_403_FORBIDDEN)
    response = SUPERPOOL_HANDLER.get_all_product_sold_by_agent_for_one_insurer(insurer_id)
    status_code = response.get('status_code')
    error = response.get('error')
    data = response.get('data')

    if status_code != 200:
        return Response(error, status.HTTP_400_BAD_REQUEST)

    return Response(data, status.HTTP_200_OK)

