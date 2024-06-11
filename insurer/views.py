from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializer import CreateInsurerSerializer, LoginInsurerSerializer
from rest_framework.response import Response
from .models import Insurer


def store_insurer_profile_pictures(profile_picture):
    return


@api_view(['POST'])
def create_insurer(request):
    serializer_class = CreateInsurerSerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        insurer_name = serializer_class.validated_data.get('username')
        serializer_class.save()
        return Response({f"Account successfully created for insurer: {insurer_name}"}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({f"The error {e.__str__()} occurred"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_insurer(request):
    serializer_class = LoginInsurerSerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        insurer_name = serializer_class.validated_data.get('username')
        insurer = Insurer.objects.get(username=insurer_name)
        auth_token = RefreshToken.for_user(insurer)

        message = {
            "login_status": True,
            "access_token": str(auth_token.access_token),
            "refresh_token": str(auth_token)
        }
        return Response(message, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({f"The error {e.__str__()} occurred"}, status=status.HTTP_400_BAD_REQUEST)


