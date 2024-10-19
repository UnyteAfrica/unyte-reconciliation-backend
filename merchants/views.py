from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from .serializers import CreateMerchantSerializer


class CreateMerchantAPIView(GenericAPIView):
    serializer_class = CreateMerchantSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'data': None, 'message': 'Merchant account created successfully'},
            status=status.HTTP_201_CREATED,
        )
