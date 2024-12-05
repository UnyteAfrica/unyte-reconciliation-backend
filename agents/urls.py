from django.urls import path

from .views import create_agent, view_claims_for_insurer, view_policies_for_insurer, view_products_for_insurer

urlpatterns = [
    path('sign-up', create_agent, name='register-agent'),
    path('products', view_products_for_insurer, name='view-products-for-insurer'),
    path('policies', view_policies_for_insurer, name='view-policies-for-insurer'),
    path('claims', view_claims_for_insurer, name='view-claims-for-insurer'),
]
