from django.urls import path

from .views import (
    get_all_products,
    get_all_claims_one_insurer,
    get_all_claims_one_merchant,
    get_all_policies_one_insurer,
    get_all_products_one_insurer,
    get_all_policies_one_merchant,
    get_all_products_one_merchant,
    get_all_product_sold_by_agent_for_one_insurer,
    get_all_product_types_sold_by_agent_for_one_insurer,
    get_all_customers_agent_sold_product_types_for_one_insurer,
)

urlpatterns = [
    path('products', get_all_products, name='get_all_products'),
    path('merchants/<merchant_id>/products', get_all_products_one_merchant, name='get-all-products-one-merchant'),
    path('merchants/<merchant_id>/policies', get_all_policies_one_merchant, name='get-all-policies-one-merchant'),
    path('merchants/<merchant_id>/claims', get_all_claims_one_merchant, name='get-all-claims-one-merchant'),
    path('insurer/<insurer_id>/products', get_all_products_one_insurer, name='get-all-products-one-insurer'),
    path('insurer/<insurer_id>/policies', get_all_policies_one_insurer, name='get-all-policies-one-insurer'),
    path('insurer/<insurer_id>/claims', get_all_claims_one_insurer, name='get-all-claims-one-insurer'),
    path('insurer/<insurer_id>/agent/products-types', get_all_product_types_sold_by_agent_for_one_insurer, name='agent_product_types'),
    path('insurer/<insurer_id>/agent/products', get_all_product_sold_by_agent_for_one_insurer, name='agent products'),
    path('insurer/<insurer_id>/agent/customers', get_all_customers_agent_sold_product_types_for_one_insurer, name='agent_customers')
]
