from django.urls import path
from . import views

urlpatterns = [
    path('sign-up', views.create_insurer, name='register_insurer'),
    path('all-agents', views.list_all_agents_for_insurer, name='all-insurer-agents'),
    path('generate-agent-sign-up', views.invite_agents, name='generate-signup-link-for-agent'),
    path('generate-agent-sign-up-csv', views.invite_agents_csv, name='generate-signup-link-for-agent-csv'),
]
