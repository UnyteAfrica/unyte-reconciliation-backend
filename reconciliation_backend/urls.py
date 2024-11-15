"""
URL configuration for reconciliation_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from django.urls import path, include
from django.contrib import admin

from rest_framework import permissions
from rest_framework.authentication import BasicAuthentication, TokenAuthentication, SessionAuthentication

schema_view = get_schema_view(
    openapi.Info(
        title='Reconciliation Dashboard API',
        default_version='v1',
        description='Reconciliation Dashboard for integrated Insurers and Agents',
        terms_of_service='https://www.google.com/policies/terms/',
        contact=openapi.Contact(email='somtochukwuuchegbu@gmail.com'),
        license=openapi.License(name='BSD License'),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    authentication_classes=[BasicAuthentication, SessionAuthentication, TokenAuthentication],
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/merchants/', include(('merchants.urls', 'merchants'), namespace='merchants')),
    path('api/insurer/', include(('insurer.urls', 'insurer'), namespace='insurer')),
    path('api/agent/', include(('agents.urls', 'agents'), namespace='agents')),
    path('api/user/', include(('user.urls', 'user'), namespace='user')),
<<<<<<< HEAD
    path('api/dashboard/', include(('superpool_proxy.urls', 'superpool_proxy'), namespace='superpool_proxy')),
=======
>>>>>>> a3ce70caa0861a9a376333afa9b3cce82b721d8a
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('docs/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('docs/json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
