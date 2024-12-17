from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from insurer.models import Insurer

from user.models import CustomUser

from merchants.models import Merchant

from .superpool_client import SuperpoolClient

SUPERPOOL_HANDLER = SuperpoolClient()
SUPERPOOL_PROXY_TAG = 'Dashboard'
PAGINATION_PAGE_SIZE = 10


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

    # paginator = PageNumberPagination()
    # paginator.page_size = PAGINATION_PAGE_SIZE
    # paginated_data = paginator.paginate_queryset(data, request)

    return Response(data, status.HTTP_200_OK)
    # return paginator.get_paginated_response(paginated_data)


@swagger_auto_schema(
    method='GET',
    operation_description='Get all products for one merchant Superpool',
    responses={200: openapi.Response('OK'), 400: 'Bad Request'},
    tags=[SUPERPOOL_PROXY_TAG],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_products_for_one_merchant(request: Request) -> Response:
    user = get_object_or_404(CustomUser, pk=request.user.id)
    if user.is_agent or user.is_insurer:
        return Response({
            'error': 'Unathorized entity access'
        }, status.HTTP_403_FORBIDDEN)
    merchant = get_object_or_404(Merchant, user=user)
    response = SUPERPOOL_HANDLER.get_all_products_for_one_merchant(merchant.tenant_id)
    status_code = response.get('status_code')
    error = response.get('error')
    data = response.get('data')

    if status_code != 200:
        return Response(error, status.HTTP_400_BAD_REQUEST)

    # paginator = PageNumberPagination()
    # paginator.page_size = PAGINATION_PAGE_SIZE
    # paginated_data = paginator.paginate_queryset(data, request)

    return Response(data, status.HTTP_200_OK)
    # return paginator.get_paginated_response(paginated_data)


@swagger_auto_schema(
    method='GET',
    operation_description='Get all policies for one merchant from Superpool',
    responses={200: openapi.Response('OK'), 400: 'Bad Request'},
    tags=[SUPERPOOL_PROXY_TAG],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_policies_for_one_merchant(request: Request) -> Response:
    user = get_object_or_404(CustomUser, pk=request.user.id)
    if user.is_agent or user.is_insurer:
        return Response({
            'error': 'Unathorized entity access'
        }, status.HTTP_403_FORBIDDEN)
    merchant = get_object_or_404(Merchant, user=user)
    response = SUPERPOOL_HANDLER.get_all_policies_for_one_merchant(merchant.tenant_id)
    status_code = response.get('status_code')
    error = response.get('error')
    data = response.get('data')

    if status_code != 200:
        return Response(error, status.HTTP_400_BAD_REQUEST)

    paginator = PageNumberPagination()
    paginator.page_size = PAGINATION_PAGE_SIZE
    paginated_data = paginator.paginate_queryset(data, request)

    return paginator.get_paginated_response(paginated_data)


@swagger_auto_schema(
    method='GET',
    operation_description='Get all claims for one merchant from Superpool',
    responses={200: openapi.Response('OK'), 400: 'Bad Request'},
    tags=[SUPERPOOL_PROXY_TAG],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_claims_for_one_merchant(request: Request) -> Response:
    user = get_object_or_404(CustomUser, pk=request.user.id)
    if user.is_agent or user.is_insurer:
        return Response({
            'error': 'Unathorized entity access'
        }, status.HTTP_403_FORBIDDEN)
    merchant = get_object_or_404(Merchant, user=user)
    response = SUPERPOOL_HANDLER.get_all_claims_for_one_merchant(merchant.tenant_id)
    status_code = response.get('status_code')
    error = response.get('error')
    data = response.get('data')

    if status_code != 200:
        return Response(error, status.HTTP_400_BAD_REQUEST)

    paginator = PageNumberPagination()
    paginator.page_size = PAGINATION_PAGE_SIZE
    paginated_data = paginator.paginate_queryset(data, request)

    return paginator.get_paginated_response(paginated_data)


@swagger_auto_schema(
    method='GET',
    operation_description='Get all policies for one insurer from Superpool',
    responses={200: openapi.Response('OK'), 400: 'Bad Request'},
    tags=[SUPERPOOL_PROXY_TAG],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_policies_one_insurer(request: Request) -> Response:
    user = get_object_or_404(CustomUser, pk=request.user.id)
    if user.is_agent or user.is_merchant:
        return Response({
            'error': 'Unathorized entity access'
        }, status.HTTP_403_FORBIDDEN)
    insurer = get_object_or_404(Insurer, user=user)
    insurer_id = insurer.insurer_id
    response = SUPERPOOL_HANDLER.get_all_policies_for_one_insurer(insurer_id)
    status_code = response.get('status_code')
    error = response.get('error')
    data = response.get('data')

    if status_code != 200:
        return Response(error, status.HTTP_400_BAD_REQUEST)

    paginator = PageNumberPagination()
    paginator.page_size = PAGINATION_PAGE_SIZE
    paginated_data = paginator.paginate_queryset(data, request)

    return paginator.get_paginated_response(paginated_data)


@swagger_auto_schema(
    method='GET',
    operation_description='Get all claims for one insurer from Superpool',
    responses={200: openapi.Response('OK'), 400: 'Bad Request'},
    tags=[SUPERPOOL_PROXY_TAG],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_claims_one_insurer(request: Request) -> Response:
    user = get_object_or_404(CustomUser, pk=request.user.id)
    if user.is_agent or user.is_merchant:
        return Response({
            'error': 'Unathorized entity access'
        }, status.HTTP_403_FORBIDDEN)
    insurer = get_object_or_404(Insurer, user=user)
    insurer_id = insurer.insurer_id
    response = SUPERPOOL_HANDLER.get_all_claims_for_one_insurer(insurer_id)
    status_code = response.get('status_code')
    error = response.get('error')
    data = response.get('data')

    if status_code != 200:
        return Response(error, status.HTTP_400_BAD_REQUEST)

    paginator = PageNumberPagination()
    paginator.page_size = PAGINATION_PAGE_SIZE
    paginated_data = paginator.paginate_queryset(data, request)

    return paginator.get_paginated_response(paginated_data)


@swagger_auto_schema(
    method='GET',
    operation_description='Get all product_types sold by agents for one insurer from Superpool',
    responses={200: openapi.Response('OK'), 400: 'Bad Request'},
    tags=[SUPERPOOL_PROXY_TAG],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_products_for_one_insurer(request: Request) -> Response:
    user = get_object_or_404(CustomUser, pk=request.user.id)
    if user.is_agent or user.is_merchant:
        return Response({
            'error': 'Unathorized entity access'
        }, status.HTTP_403_FORBIDDEN)
    insurer = get_object_or_404(Insurer, user=user)
    insurer_id = insurer.insurer_id
    response = SUPERPOOL_HANDLER.get_all_products_for_one_insurer(insurer_id)
    status_code = response.get('status_code')
    error = response.get('error')
    data = response.get('data')

    if status_code != 200:
        return Response(error, status.HTTP_400_BAD_REQUEST)

    # paginator = PageNumberPagination()
    # paginator.page_size = PAGINATION_PAGE_SIZE
    # paginated_data = paginator.paginate_queryset(data, request)

    return Response(data, status.HTTP_200_OK)
    # return paginator.get_paginated_response(paginated_data)
