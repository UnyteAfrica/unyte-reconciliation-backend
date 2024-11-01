import csv
from io import TextIOWrapper

from dotenv import find_dotenv, load_dotenv
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from user.models import CustomUser

from .utils import verify_otp, gen_sign_up_url_for_agent
from .models import Insurer, InvitedAgents, InsurerProfile
from .serializer import (
    AgentSerializer,
    CustomAgentSerializer,
    CreateInsurerSerializer,
    UploadCSVFileSerializer,
    InsurerProfileSerializer,
    UpdateProfileImageSerializer,
)
from .response_serializers import (
    SuccessfulCreateInsurerSerializer,
    SuccessfulListAllAgentsSerializer,
    SuccessfulInsurerAgentSignupSerializer,
    SuccessfulInsurerAgentSignupCSVSerializer,
)

load_dotenv(find_dotenv())


@swagger_auto_schema(
    method='POST',
    request_body=CreateInsurerSerializer,
    operation_description='Create new insurer',
    responses={201: openapi.Response('Created', SuccessfulCreateInsurerSerializer), 400: 'Bad Request'},
    tags=['Insurer'],
)
@api_view(['POST'])
def create_insurer(request) -> Response:
    """
    Create insurer by using params from CreateInsurerSerializer
    :param request:
    :return: Response
    """
    serializer_class = CreateInsurerSerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        business_name = serializer_class.validated_data.get('business_name')
        insurer_email = serializer_class.validated_data.get('email')

        """
        Send email to insurer including otp.
        """
        serializer_class.save()
        insurer = CustomUser.objects.get(email=insurer_email)

        current_year = timezone.now().year
        company_name = business_name

        context = {
            'current_year': current_year,
            'company_name': company_name,
        }

        html_message = render_to_string('welcome.html', context)

        send_mail(
            subject='Welcome email',
            message='Welcome',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.TO_EMAIL, insurer_email],
            html_message=html_message,
        )

        message = {'id': insurer.id, 'message': f'Account successfully created for user: {business_name}'}
        return Response(message, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({f'The error {e.__str__()} occurred'}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='GET',
    operation_description='View all agents invited by an Insurer',
    responses={
        200: openapi.Response(
            'OK',
            SuccessfulListAllAgentsSerializer(many=True),
        ),
        403: 'Unauthorized',
        404: 'Not Found',
        400: 'Bad Request',
    },
    tags=['Insurer'],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_all_agents_for_insurer(request):
    user_id = request.user.id
    user = get_object_or_404(CustomUser, pk=user_id)

    if not user.is_insurer:
        return Response({'error': 'This user is not an insurer'}, status.HTTP_400_BAD_REQUEST)

    insurer = get_object_or_404(Insurer, user=user)
    query_set = insurer.agent_set.all()

    serializer_class = AgentSerializer(query_set, many=True)
    return Response(serializer_class.data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='POST',
    operation_description='Generate SignUp Link for Agents',
    request_body=CustomAgentSerializer,
    responses={
        200: openapi.Response(
            'OK',
            SuccessfulInsurerAgentSignupSerializer,
        ),
        400: 'Bad Request',
        404: 'Not Found',
    },
    tags=['Insurer'],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def invite_agents(request):
    serializer_class = CustomAgentSerializer(data=request.data)
    user_id = request.user.id
    user = get_object_or_404(CustomUser, pk=user_id)

    if not user.is_insurer:
        return Response({'error': 'This user is not an insurer'}, status.HTTP_400_BAD_REQUEST)

    insurer = get_object_or_404(Insurer, user=user)
    unyte_unique_insurer_id = insurer.unyte_unique_insurer_id

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)

    agent_list = serializer_class.validated_data.get('agents_list')
    email_recipients = []

    relative_link = reverse('agents:register_agent')
    relative_link = relative_link.replace('/api/', '/')
    link = gen_sign_up_url_for_agent(relative_link, unyte_unique_insurer_id)

    current_year = timezone.now().year
    company_name = insurer.business_name

    for agent in agent_list:
        name = agent['names']
        email = agent['emails']

        context = {
            'current_year': current_year,
            'company_name': company_name,
            'unyte_unique_insurer_id': unyte_unique_insurer_id,
            'name': name,
        }
        invited_agents = InvitedAgents.objects.create(
            insurer=insurer,
            agent_email=email
        )
        invited_agents.save()
        html_message = render_to_string('invitation.html', context)
        email_recipients.append(email)
        """
        Sends email to the email of agents
        """
        send_mail(
            subject='Agent SignUp Link',
            message=f'{link}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=email_recipients,
            html_message=html_message,
        )
        email_recipients.pop(0)

    return Response({'message': f'Link generated: {link}'})


@swagger_auto_schema(
    method='POST',
    operation_description='Generate SignUp Link for Agents through CSV file',
    responses={
        200: openapi.Response(
            'OK',
            SuccessfulInsurerAgentSignupCSVSerializer,
        ),
        400: 'Bad Request',
        404: 'Not Found',
    },
    tags=['Insurer'],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def invite_agents_csv(request):
    user = get_object_or_404(CustomUser, pk=request.user.id)
    if not user.is_insurer:
        return Response({'error': 'This user is not an insurer'}, status.HTTP_400_BAD_REQUEST)

    serializer_class = UploadCSVFileSerializer(data=request.data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)

    insurer = get_object_or_404(Insurer, user=user)
    unyte_unique_insurer_id = insurer.unyte_unique_insurer_id
    company_name = insurer.business_name
    current_year = timezone.now().year

    relative_link = reverse('agents:register_agent')
    relative_link = relative_link.replace('/api/', '/')
    link = gen_sign_up_url_for_agent(relative_link, unyte_unique_insurer_id)

    try:
        otp = serializer_class.validated_data.get('otp')

        if otp != insurer.otp:
            return Response({'error': 'Invalid OTP'}, status.HTTP_400_BAD_REQUEST)

        otp_created_time = insurer.otp_created_at
        verify = verify_otp(otp_created_time)

        if not verify:
            message = {'error': 'OTP has expired'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['agents_csv']
        file_extension = file.name.split('.')[-1]
        if file_extension != 'csv':
            return Response(
                {'error': f'Unacceptable file format {file_extension}. Must be a csv file'},
                status.HTTP_400_BAD_REQUEST,
            )
        csv_file = TextIOWrapper(file.file, encoding='utf-8')
        csv_reader = csv.reader(csv_file, delimiter=',')
        all_rows = list(csv_reader)
        for agent in range(len(all_rows)):
            if agent == 0:
                pass
            else:
                agent_name = all_rows[agent][0]
                agent_email = all_rows[agent][1]

                context = {
                    'current_year': current_year,
                    'company_name': company_name,
                    'unyte_unique_insurer_id': unyte_unique_insurer_id,
                    'name': agent_name,
                }
                html_message = render_to_string('invitation.html', context)
                invited_agents = InvitedAgents.objects.create(
                    insurer=insurer,
                    agent_email=agent_email
                )
                invited_agents.save()
                """
                Sends email to the email of agents
                """
                send_mail(
                    subject='Agent SignUp Link',
                    message=f'{link}',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[agent_email, settings.TO_EMAIL],
                    html_message=html_message,
                )
        return Response({'message': f'Successfully sent out invite links to {len(all_rows) - 1} agent(s)'})
    except Exception as e:
        return Response({'error': f'{e.__str__()}'}, status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='GET',
    operation_description='View Insurer Profile',
    responses={200: 'OK', 400: 'Bad Request', 404: 'Not Found'},
    tags=['Insurer'],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_insurer_profile(request) -> Response:
    user = get_object_or_404(CustomUser, pk=request.user.id)
    insurer = get_object_or_404(Insurer, user=user)
    insurer_profile = get_object_or_404(InsurerProfile, insurer=insurer)

    insurer_email = user.email
    insurer_business_name = insurer.business_name
    insurer_profile_pic = insurer_profile.profile_image.url

    data = {'email': insurer_email, 'business_name': insurer_business_name, 'profile_image': str(insurer_profile_pic)}

    serializer_class = InsurerProfileSerializer(data=data)

    if not serializer_class.is_valid():
        return Response({'error': serializer_class.errors}, status.HTTP_400_BAD_REQUEST)

    return Response(serializer_class.data, status.HTTP_200_OK)


@swagger_auto_schema(
    method='POST',
    operation_description='Create Policy',
    request_body=UpdateProfileImageSerializer,
    responses={200: 'OK', 400: 'Bad Request', 404: 'Not Found'},
    tags=['Insurer'],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_profile_image(request) -> Response:
    user = get_object_or_404(CustomUser, pk=request.user.id)

    if not user.is_insurer:
        return Response({'error': 'This user is not an insurer'}, status.HTTP_400_BAD_REQUEST)

    insurer = get_object_or_404(Insurer, user=user)
    insurer_profile_obj = get_object_or_404(InsurerProfile, insurer=insurer)
    serializer_class = UpdateProfileImageSerializer(insurer_profile_obj, data=request.data, partial=True)
    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)

    serializer_class.save()
    return Response({'message': 'Profile image updated'}, status.HTTP_200_OK)
