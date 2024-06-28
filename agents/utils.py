import pyotp
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())


def send_otp(request, insurer_email: str) -> None:
    totp = pyotp.TOTP(pyotp.random_base32(), interval=60)
    otp = totp.now()
    request.session['agent_otp_secret_key'] = totp.secret
    valid_date = datetime.now() + timedelta(minutes=1)
    request.session['agent_otp_valid_date'] = str(valid_date)

    if os.getenv('ENV') != 'dev':
        send_mail(
            subject='Verification email',
            message=f'{otp}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[insurer_email],
        )
        return None

    # Send emails to registered insurer email and settings.TO_EMAIL defined email for testing.
    send_mail(
        subject='Verification email',
        message=f'{otp}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.TO_EMAIL, insurer_email],
    )
    return None


def verify_otp(request, otp: str) -> bool:
    otp_secret_key = request.session.get('agent_otp_secret_key')
    otp_valid_until = request.session.get('agent_otp_valid_date')

    if otp_secret_key and otp_valid_until is None:
        print("Invalid OTP secret")

    valid_until = datetime.now()
    totp = pyotp.TOTP(otp_secret_key, interval=60)

    if valid_until > datetime.now():
        print("OTP has expired")
        return False

    if not totp.verify(otp):
        print("Invalid OTP value")
        return False

    del otp_secret_key
    del otp_valid_until

    return True
