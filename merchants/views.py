from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from .serializers import CreateMerchantSerializer, MerchantSerializer


class CreateMerchantAPIView(GenericAPIView):
    serializer_class = CreateMerchantSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        merchant = serializer.save()

        merchant_serializer = MerchantSerializer(merchant)
        return Response(
            {'data': merchant_serializer.data, 'message': 'Merchant account created successfully'},
            status=status.HTTP_201_CREATED,
        )
