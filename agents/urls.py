from django.urls import path

from .views import (
    create_agent,
    sell_motor_policy,
    sell_travel_policy,
    generate_bike_quotes,
    sell_shipment_policy,
    sell_travel_policy,
    generate_bike_quotes,
    generate_motor_quotes,
    generate_gadget_quotes,
    generate_travel_quotes,
    get_bike_quote_response,
    view_claims_for_insurer,
    generate_shipment_quotes,
    get_motor_quote_response,
    get_gadget_quote_response,
    get_travel_quote_response,
    view_policies_for_insurer,
    view_products_for_insurer,
    get_shipment_quote_response,
)

urlpatterns = [
    path('sign-up', create_agent, name='register-agent'),
    path('products', view_products_for_insurer, name='view-products-for-insurer'),
    path('policies', view_policies_for_insurer, name='view-policies-for-insurer'),
    path('claims', view_claims_for_insurer, name='view-claims-for-insurer'),
    path('quotes/travel/<product_name>', generate_travel_quotes, name='generate quotes for insurer'),
    path('quotes/gadget/<product_name>', generate_gadget_quotes, name='generate quotes for insurer'),
    path('quotes/motor/<product_name>', generate_motor_quotes, name='generate quotes for insurer'),
    path('quotes/bike/<product_name>', generate_bike_quotes, name='generate quotes for insurer'),
    path('quotes/shipment/<product_name>', generate_shipment_quotes, name='generate quotes for insurer'),

    path('response/travel', get_travel_quote_response, name='response for travel quotes'),
    path('response/gadget', get_gadget_quote_response, name='response for gadget quotes'),
    path('response/motor', get_motor_quote_response, name='response for motor quotes'),
    path('response/bike', get_bike_quote_response, name='response for bike quotes'),
    path('response/shipment', get_shipment_quote_response, name='response for shipmen quotes'),

    path('sell-policy/travel', sell_travel_policy, name='sell travel policy'),
    path('sell-policy/shipment', sell_shipment_policy, name='sell shipment policy'),
    path('sell-policy/motor', sell_motor_policy, name='sell motor policy'),
]
