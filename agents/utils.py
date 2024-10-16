import os
from datetime import datetime

import pyotp
from dotenv import find_dotenv, load_dotenv

from django.utils import timezone

from rest_framework.exceptions import APIException

load_dotenv(find_dotenv())


FRONTED_URL = os.getenv('FRONTEND_URL', 'unyte-reconciliations-frontend-dev-ynoamqpukq-uc.a.run.app')


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
    return totp.now()


def verify_otp(otp_created_at) -> bool:
    current_time = timezone.now().time()
    today = timezone.now().today()

    otp_created_time_datetime = datetime.combine(today, otp_created_at)
    current_datetime = datetime.combine(today, current_time)

    time_delta = current_datetime - otp_created_time_datetime

    return not time_delta.total_seconds() >= 120


def gen_absolute_url(id_base64, token):
    if os.getenv('ENV') != 'dev':
        return f'https://{FRONTED_URL}/agent/reset-password/{id_base64}/{token}'
    return f'http://{FRONTED_URL}/agent/reset-password/{id_base64}/{token}'


def generate_unyte_unique_agent_id(first_name: str, bank_account: str) -> str:
    first_char = len(bank_account) - 4
    last_char = len(bank_account)
    return f'{"".join(first_name.split())}+{bank_account[first_char:last_char]}+unyte.com'
