from rest_framework_simplejwt.tokens import RefreshToken

from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import smart_bytes
from django.template.loader import render_to_string
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from rest_framework import status
from rest_framework.response import Response

from agents.utils import verify_otp, generate_otp, gen_absolute_url
from agents.models import Agent, AgentProfile

from user.models import CustomUser
from user.serializer import ViewAgentDetailsSerializer, ViewAgentProfileSerializer


def agent_sign_in(user: CustomUser, agent_email: str) -> Response:
    try:
        agent = get_object_or_404(Agent, user=user)
        otp = generate_otp()
        agent.otp = otp
        agent.otp_created_at = timezone.now().time()

        name = f"{agent.first_name} {agent.last_name}"
        current_year = timezone.now().year

        agent.save()

        context = {"name": name, "current_year": current_year, "otp": otp}

        html_message = render_to_string("agents/otp.html", context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject="Login OTP",
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.TO_EMAIL, agent_email],
            html_message=html_message,
        )

        message = {"message": "OTP has been sent out to your email"}

        return Response(message, status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status.HTTP_400_BAD_REQUEST)


def agent_verify_otp_token(user: CustomUser, otp: str) -> Response:
    try:
        agent = Agent.objects.get(user=user)
        agent_otp = agent.otp

        if agent_otp != otp:
            message = {"error": "Incorrect OTP"}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        otp_created_time = agent.otp_created_at
        verify = verify_otp(otp_created_time)

        if not verify:
            message = {"error": "OTP has expired"}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        auth_token = RefreshToken.for_user(user)

        message = {
            "login_status": True,
            "AGENT_ID": agent.id,
            "access_token": str(auth_token.access_token),
            "refresh_token": str(auth_token),
        }

        return Response(message, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status.HTTP_400_BAD_REQUEST)


def agent_forget_email_password(user: CustomUser, agent_email: str) -> Response:
    agent = get_object_or_404(Agent, user=user)
    try:
        id_base64 = urlsafe_base64_encode(smart_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        absolute_url = gen_absolute_url(id_base64, token)
        name = f"{agent.first_name} + {agent.last_name}"

        context = {
            "agent_name": name,
            "url": absolute_url,
            "id": id_base64,
            "token": token,
            "current_year": timezone.now().year,
        }

        html_message = render_to_string("agents/forgot-password.html", context=context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject="Forgot Password",
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.TO_EMAIL, agent_email],
            html_message=html_message,
        )

        response = {"message": "Confirmation email sent"}
        return Response(response, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


def agent_reset_password(user: CustomUser, insurer_email: str) -> Response:
    try:
        if not user.is_agent:
            return Response({"error": "This user is not an agent"}, status.HTTP_400_BAD_REQUEST)

        agent = get_object_or_404(Agent, user=user)

        otp = generate_otp()
        agent.otp = otp
        agent.otp_created_at = timezone.now().time()
        name = f"{agent.first_name} {agent.last_name}"
        current_year = timezone.now().year

        agent.save()

        context = {"name": name, "current_year": current_year, "otp": otp}

        html_message = render_to_string("otp.html", context)

        send_mail(
            subject="Request New OTP",
            message=f"{otp}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.TO_EMAIL, insurer_email],
            html_message=html_message,
        )

        return Response({"message": "New OTP sent out!"}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status.HTTP_400_BAD_REQUEST)


def agent_view_details(user: CustomUser) -> Response:
    agent = get_object_or_404(Agent, user=user)

    data = {
        "id": agent.id,
        "email": user.email,
        "first_name": agent.first_name,
        "last_name": agent.last_name,
        "middle_name": agent.middle_name,
    }
    serializer_class = ViewAgentDetailsSerializer(data=data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)

    return Response(serializer_class.data, status.HTTP_200_OK)


def agent_view_profile(user: CustomUser) -> Response:
    agent = get_object_or_404(Agent, user=user)
    agent_profile = get_object_or_404(AgentProfile, agent=agent)

    data = {
        "id": agent.id,
        "email": user.email,
        "first_name": agent.first_name,
        "last_name": agent.last_name,
        "middle_name": agent.middle_name,
        "profile_picture": agent_profile.profile_image.path,
    }
    serializer_class = ViewAgentProfileSerializer(data=data)

    if not serializer_class.is_valid():
        return Response(serializer_class.errors, status.HTTP_400_BAD_REQUEST)

    return Response(serializer_class.data, status.HTTP_200_OK)
