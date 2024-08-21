from django.urls import path
from . import views

urlpatterns = [
    path('/create-gamp-users/<int:count>', views.create_gamp_users, name='create arbitrary users'),
]