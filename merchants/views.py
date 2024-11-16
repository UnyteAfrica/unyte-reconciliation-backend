from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from .serializers import MerchantSerializer, CreateMerchantSerializer


class CreateMerchantAPIView(GenericAPIView):
    serializer_class = CreateMerchantSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        merchant = serializer.save()

        merchant_serializer = MerchantSerializer(merchant)
        try:
            merchant_name = merchant_serializer.data.get('name')
            merchant_email = merchant_serializer.data.get('email_address')

            """
            Send email to insurer including otp.
            """
            current_year = timezone.now().year

            context = {
                'current_year': current_year,
                'merchant_name': merchant_name,
            }

            html_message = render_to_string('merchants/welcome.html', context)

            send_mail(
                subject='Welcome email',
                message='Welcome',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.TO_EMAIL, merchant_email],
                html_message=html_message,
            )
            return Response(merchant_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({f'The error {e.__str__()} occurred'}, status=status.HTTP_400_BAD_REQUEST)
