from django.shortcuts import render
from .serializers import GampUserSerializer, GampDeviceSerializer, GampClaimSerializer
from .models import GampArbitraryUser
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from faker import Faker


@swagger_auto_schema(
    method='GET',
    operation_description='Create Gamp User(s)',
    responses={
        '201': "Created",
        '400': 'Bad Request'
    },
    tags=['Gamp']
)
@api_view(['GET'])
def create_gamp_users(request, count) -> Response:
    print(request.query_params)
    fake = Faker()
    print(count)

    for _ in range(count):
        GampArbitraryUser.objects.create(
            uuid=fake.uuid4(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone_number=fake.phone_number(),
            email=fake.email()
        )
    try:
        all_users = GampArbitraryUser.objects.all()
        queryset = GampUserSerializer(all_users, many=True)
        return Response(queryset.data, status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "error": f"The error '{e}' occurred"
        })
