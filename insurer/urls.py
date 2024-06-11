from django.urls import path
from . import views


urlpatterns = [
    path('sign-up', views.create_insurer, name='register insurer'),
    path('sign-in', views.login_insurer, name='login insurer'),
]
