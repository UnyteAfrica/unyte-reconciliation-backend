from django.urls import path

from . import views

urlpatterns = [
    path('sign-up', views.create_agent, name='register_agent'),
]
