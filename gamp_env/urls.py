from django.urls import path
from . import views

urlpatterns = [
    path('create-gamp-users/<int:count>', views.create_gamp_users, name='create arbitrary users'),
    path('create-gamp-policies/<int:count>/<str:insurer>', views.create_policy_with_insurer, name='create arbitrary '
                                                                                                  'policies'),
    path('create-gamp-products/<int:count>', views.create_products_for_policy, name='create arbitrary '
                                                                                                  'products'),
    path('view-gamp-insurer/<str:insurer>', views.view_product_by_insurer, name='view insurer policies'),
    path('customer-buy-products', views.customer_purchase_policy, name='customer buy policies'),
    path('view-all-policies-bought-by-customer', views.view_policies_customer_bought, name='policies bought by customer'),
]
