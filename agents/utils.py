import pyotp
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
import os

from rest_framework.exceptions import APIException

load_dotenv(find_dotenv())


class CustomValidationError(APIException):
    status_code = 400
    default_detail = 'Invalid input.'
    default_code = 'invalid'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = {'error': self.default_detail}
        self.detail = detail


def generate_otp() -> str:
    totp = pyotp.TOTP(pyotp.random_base32(), interval=60)
    otp = totp.now()

    return otp


def verify_otp(otp_created_at) -> bool:
    current_time = datetime.now().time()
    today = datetime.now().today()

    otp_created_time_datetime = datetime.combine(today, otp_created_at)
    current_datetime = datetime.combine(today, current_time)

    time_delta = current_datetime - otp_created_time_datetime
    print(time_delta.total_seconds())

    if time_delta.total_seconds() >= 120:
        return False

    return True


def gen_absolute_url(current_site, relative_link, token):
    if os.getenv('ENV') != 'dev':
        return f'https://{current_site}{relative_link}?token={str(token)}'
    return f'http://{current_site}{relative_link}?token={str(token)}'
