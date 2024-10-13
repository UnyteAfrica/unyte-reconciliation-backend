from django.urls import path
from .views import (
    sign_in,
    verify_otp,
    forgot_email_password,
    password_token_check,
    reset_password,
    request_new_otp
)

urlpatterns = [
    path('sign-in', sign_in, name='user_sign_in_endpoint'),
    path('verify-otp', verify_otp, name='verify_otp_endpoint'),
    path('forgot-password', forgot_email_password, name='forgot_password_endpoint'),
    path('password-reset/<id_base64>/<token>', password_token_check, name='password_token_check_endpoint'),
    path('reset-password', reset_password, name='rest_password_endpoint'),
    path('request-new-otp', request_new_otp, name='request_new_otp_endpoint'),
]