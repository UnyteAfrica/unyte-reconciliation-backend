from django.urls import path

from .views import CreateMerchantAPIView

urlpatterns = [
    path('sign-up', CreateMerchantAPIView.as_view(), name='create-merchant'),
]
