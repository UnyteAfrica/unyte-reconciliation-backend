from django.urls import path
from . import views


urlpatterns = [
    path('sign-up', views.create_insurer, name='register_insurer'),
    path('sign-in', views.login_insurer, name='login_insurer'),
    path('verify-otp', views.verify_otp_token, name='verify_otp'),
    path('new-otp', views.request_new_otp, name='get_new_otp')
]
