from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.html import strip_tags
from django.template.loader import render_to_string

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from insurer.models import Insurer, InvitedAgents

from user.models import CustomUser

from .utils import generate_otp, generate_unyte_unique_agent_id
from .models import Agent
from .serializer import CreateAgentSerializer
from .response_serializers import (
    SuccessfulCreateAgentSerializer,
)


@swagger_auto_schema(
    method='POST',
    manual_parameters=[
        openapi.Parameter('invite', openapi.IN_QUERY, description='Insurer unique unyte id', type=openapi.TYPE_STRING),
    ],
    request_body=CreateAgentSerializer,
    operation_description='Create New Agent',
    responses={
        '201': openapi.Response(
            'Created',
            SuccessfulCreateAgentSerializer,
        ),
        '400': 'Bad Request',
    },
    tags=['Agent'],
)
@api_view(['POST'])
def create_agent(request) -> Response:
    serializer_class = CreateAgentSerializer(data=request.data)

    if request.query_params.get('invite') is None:
        return Response({'error': "Can't find your Insurer's identifier"}, status.HTTP_400_BAD_REQUEST)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        uuid = request.query_params.get('invite')
        insurer = get_object_or_404(Insurer, unyte_unique_insurer_id=uuid)

        user_email = serializer_class.validated_data.get('email')
        user_password = serializer_class.validated_data.get('password')

        """
        Check to see if the agent who is attempting to register is under the list of invited agents.
        """
        insurer_invited_agents_objs = InvitedAgents.objects.filter(insurer=insurer).values()
        insurer_invited_agents = [email.get('agent_email') for email in insurer_invited_agents_objs]

        if user_email not in insurer_invited_agents:
            return Response({
                "error": "Unauthorized email. No Insurer has invited an agent with this email"
            }, status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.create_user(email=user_email, password=user_password, is_agent=True)
        user.save()

        agent_data = serializer_class.validated_data

        first_name = agent_data.get('first_name')
        last_name = agent_data.get('last_name')
        bank_account = agent_data.get('bank_account')
        middle_name = agent_data.get('middle_name')
        home_address = agent_data.get('home_address')
        bvn = agent_data.get('bvn')
        agent_data['affiliated_company'] = insurer

        uuad = generate_unyte_unique_agent_id(first_name, bank_account)

        agent = Agent.objects.create(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            home_address=home_address,
            bank_account=bank_account,
            bvn=bvn,
            affiliated_company=insurer,
            unyte_unique_agent_id=uuad,
            otp=generate_otp(),
            user=user,
            otp_created_at=timezone.now().time(),
        )
        agent.save()
        current_year = timezone.now().year

        context = {'current_year': current_year, 'name': f'{first_name} {last_name}'}
        html_message = render_to_string('agents/welcome.html', context=context)
        plain_html_message = strip_tags(html_message)

        send_mail(
            subject='Welcome email',
            message=plain_html_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.TO_EMAIL, user_email],
            html_message=html_message,
        )

        message = {'id': agent.id, 'message': f'Account successfully created for {first_name} {last_name}'}
        return Response(message, status=status.HTTP_201_CREATED)

    except Exception as e:
        message = {'error': e.__str__()}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
