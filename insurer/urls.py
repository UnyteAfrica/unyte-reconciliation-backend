from django.urls import path
from . import views

urlpatterns = [
    path('sign-up', views.create_insurer, name='register_insurer'),
    path('sign-in', views.login_insurer, name='login_insurer'),
    path('verify-otp', views.verify_otp_token, name='verify_otp'),
    path('password-reset', views.reset_password, name='reset_password'),
    path('forgot-password', views.forgot_password_email, name='forgot-password'),
    path('new-otp', views.request_new_otp, name='request_new_otp'),
    path('password-reset/<id_base64>/<token>', views.password_token_check, name='password-reset-confirm'),
    path('details', views.view_insurer, name='view-insurer'),
    path('all-agents', views.list_all_agents_for_insurer, name='all-insurer-agents'),
    path('create-product', views.create_product, name='create-product'),
    path('create-product-types-for-products/<str:policy_id>', views.create_products_for_policy, name='create product for policy'),
    path('view-all-products', views.view_all_products, name='view-all-policies'),
    path('view-all-policies', views.view_all_policies, name='view-sold-policies'),
    path('view-all-policies-date-range', views.view_sold_products_with_date_params, name='view-all-policies-in-a-date-range'),
    path('view-products-an-agent-sold/<int:agent_id>', views.view_products_an_agent_has_sold, name='view-sold-policies'),
    path('generate-agent-sign-up', views.generate_sign_up_link_for_agent, name='generate-signup-link-for-agent'),
    path('insurer-profile', views.view_insurer_profile, name='insurer-profile'),
    path('refresh-access-token', views.refresh_access_token, name='reset-access-token'),
    path('update-profile-picture', views.update_profile_image, name='update-profile-picture'),
]
