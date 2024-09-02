from django.urls import path
from . import views

urlpatterns = [
    path('sign-up', views.create_agent, name='register_agent'),
    path('sign-in', views.login_agent, name='login_agent'),
    path('verify-otp', views.verify_otp_token, name='verify_otp'),
    path('password-reset', views.reset_password, name='reset_password'),
    path('forgot-password', views.forgot_password_email, name='forgot-password'),
    path('new-otp', views.request_new_otp, name='request_new_otp'),
    path('password-reset/<id_base64>/<token>', views.password_token_check, name='password-reset-confirm'),
    path('details', views.view_agent_details, name='agent-details'),
    path('sell-product', views.agent_sell_product, name='claim-policy'),
    path('view-all-products', views.view_all_products, name='view-all-products'),
    path('view-all-policies', views.view_all_policies, name='view-all-policies'),
    path('agent-profile', views.view_agent_profile, name='agent-profile'),
    path('refresh-access-token', views.refresh_access_token, name='reset-access-token')
    # path('view-all-claimed-policies', views.view_all_claimed_policies, name='view-all-claimed-policies'),
    # path('claim-policy', views.agent_claim_policy, name='claim-policy'),
]

