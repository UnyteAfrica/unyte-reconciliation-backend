from django.urls import path
from . import views

urlpatterns = [
    path('create-gamp-users/<int:count>', views.create_gamp_users, name='create arbitrary users'),
    path('create-gamp-policies/<int:count>/<str:insurer>', views.create_policy_with_insurer, name='create arbitrary '
                                                                                                  'policies'),
    path('create-gamp-products/<int:count>', views.create_products_for_policy, name='create arbitrary '
                                                                                                  'products'),
    path('view-gamp-insurer/policies/<str:policy_uuid>', views.view_policies, name='view insurer policies')
]
