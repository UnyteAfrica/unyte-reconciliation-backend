from django.urls import path
from . import views

urlpatterns = [
    path('sign-up', views.create_agent, name='register_agent'),
    path('sign-in', views.login_agent, name='login_agent'),
    path('verify-otp', views.verify_otp_token, name='verify_otp'),
    path('password-reset', views.reset_password, name='reset_password'),
    path('confirm-email', views.forgot_password_email, name='confirm_email'),
    path('new-otp', views.request_new_otp, name='request_new_otp')
]

