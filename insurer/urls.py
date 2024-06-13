from django.urls import path
from . import views


urlpatterns = [
    path('sign-up', views.create_insurer, name='register insurer'),
    path('sign-in', views.login_insurer, name='login insurer'),
    path('verify-otp', views.verify_otp_token, name='verify otp'),
    path('new-otp', views.request_new_otp, name='get new otp')
]
