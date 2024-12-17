from django.urls import path

from .views import (
    bike_policy,
    create_agent,
    device_policy,
    shipment_policy,
    generate_motor_quotes,
    generate_travel_quotes,
    view_claims_for_insurer,
    view_policies_for_insurer,
    view_products_for_insurer,
)

urlpatterns = [
    path('sign-up', create_agent, name='register-agent'),
    path('products', view_products_for_insurer, name='view-products-for-insurer'),
    path('policies', view_policies_for_insurer, name='view-policies-for-insurer'),
    path('claims', view_claims_for_insurer, name='view-claims-for-insurer'),
    path('policy/travel/<product_name>', generate_travel_quotes, name='generate quotes for insurer'),
    path('policy/device', device_policy, name='generate quotes for insurer'),
    path('policy/motor/<product_name>', generate_motor_quotes, name='generate quotes for insurer'),
    path('policy/bike', bike_policy, name='generate quotes for insurer'),
    path('policy/shipment', shipment_policy, name='generate quotes for insurer')
]
