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
    path('<pk>', views.view_insurer, name='view-insurer'),
    path('<pk>/all-agents', views.list_all_agents_for_insurer, name='all-insurer-agents'),
    path('<int:pk>/claim-policy', views.insurer_claim_policy, name='claim-policy'),
    path('<int:pk>/sell-policy', views.insurer_sell_policy, name='claim-policy'),
    path('<int:pk>/view-all-policies', views.view_all_policies, name='view-all-policies'),
    path('<int:pk>/view-sold-policies', views.view_all_sold_policies, name='view-sold-policies'),
    path('<int:pk>/gen-agent-sign-up', views.generate_sign_up_link_for_agent, name='generate-signup-link-for-agent'),
    path('<int:pk>/insurer-profile', views.view_insurer_profile, name='insurer-profile')
]
