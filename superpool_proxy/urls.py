from django.urls import path

from .views import (
    get_all_products,
    get_all_claims_one_insurer,
    get_all_claims_one_merchant,
    get_all_policies_one_insurer,
    get_all_products_one_insurer,
    get_all_policies_one_merchant,
    get_all_products_one_merchant,
)

urlpatterns = [
    path('get-all-products', get_all_products, name='get_all_products'),
    path('get-all-products-one-merchant/<merchant_id>', get_all_products_one_merchant, name='get-all-products-one-merchant'),  # noqa: E501
    path('get-all-policies-one-merchant/<merchant_id>', get_all_policies_one_merchant, name='get-all-policies-one-merchant'),  # noqa: E501
    path('get-all-claims-one-merchant/<merchant_id>', get_all_claims_one_merchant, name='get-all-claims-one-merchant'),
    path('get-all-products-one-insurer/<insurer_id>', get_all_products_one_insurer, name='get-all-products-one-insurer'),  # noqa: E501
    path('get-all-policies-one-insurer/<insurer_id>', get_all_policies_one_insurer, name='get-all-policies-one-insurer'),  # noqa: E501
    path('get-all-claims-one-insurer/<insurer_id>', get_all_claims_one_insurer, name='get-all-claims-one-insurer'),
]
