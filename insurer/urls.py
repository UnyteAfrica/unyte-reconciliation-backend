from django.urls import path
from . import views


urlpatterns = [
    path('sign-up', views.create_insurer, name='register_insurer'),
    path('sign-in', views.login_insurer, name='login_insurer'),
    path('verify-otp', views.verify_otp_token, name='verify_otp'),
    path('verify-insurer', views.verify_insurer, name='verify_insurer'),
    path('password-reset', views.reset_password, name='reset_password'),
    path('confirm-email', views.forgot_password_email, name='confirm_email'),
    path('request-new-otp', views.request_new_otp, name='request_new_otp')
]
