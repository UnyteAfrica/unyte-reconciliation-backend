from django.urls import path

from .views import (
    get_all_products,
    get_all_claims_one_insurer,
    get_all_policies_one_insurer,
    get_all_claims_for_one_merchant,
    get_all_products_for_one_insurer,
    get_all_policies_for_one_merchant,
    get_all_products_for_one_merchant,
)

urlpatterns = [
    path('products', get_all_products, name='get_all_products'),
    path('merchants/products', get_all_products_for_one_merchant, name='get-all-products-one-merchant'),
    path('merchants/policies', get_all_policies_for_one_merchant, name='get-all-policies-one-merchant'),
    path('merchants/claims', get_all_claims_for_one_merchant, name='get-all-claims-one-merchant'),
    path('insurer/policies', get_all_policies_one_insurer, name='get-all-policies-one-insurer'),
    path('insurer/claims', get_all_claims_one_insurer, name='get-all-claims-one-insurer'),
    path('insurer/products', get_all_products_for_one_insurer, name='get-all-claims-one-insurer'),
]
