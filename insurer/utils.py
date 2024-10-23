import os
from datetime import datetime

import pyotp
from dotenv import find_dotenv, load_dotenv

from django.utils import timezone

from rest_framework.exceptions import APIException

load_dotenv(find_dotenv())


FRONTED_URL = os.getenv('FRONTEND_URL', 'unyte-reconciliations-frontend-dev-ynoamqpukq-uc.a.run.app')


def generate_otp() -> str:
    totp = pyotp.TOTP(pyotp.random_base32(), interval=60)
    return totp.now()


class CustomValidationError(APIException):
    status_code = 400
    default_detail = 'Invalid input.'
    default_code = 'invalid'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = {'error': self.default_detail}
        self.detail = detail


def verify_otp(otp_created_at) -> bool:
    current_time = timezone.now().time()
    today = timezone.now().today()

    otp_created_time_datetime = datetime.combine(today, otp_created_at)
    current_datetime = datetime.combine(today, current_time)

    time_delta = current_datetime - otp_created_time_datetime

    return not time_delta.total_seconds() >= 120


def gen_absolute_url(id_base64, token):
    if os.getenv('ENV') != 'dev':
        return f'https://{FRONTED_URL}/company/reset-password/{id_base64}/{token}'
    return f'http://{FRONTED_URL}/company/reset-password/{id_base64}/{token}'


def gen_sign_up_url_for_agent(relative_link, unyte_unique_insurer_id):
    if os.getenv('ENV') != 'dev':
        return f'https://{FRONTED_URL}{relative_link}?invite={unyte_unique_insurer_id!s}'
    return f'http://{FRONTED_URL}{relative_link}?invite={unyte_unique_insurer_id!s}'


def generate_unyte_unique_insurer_id(business_name: str, business_reg_num: str) -> str:
    first_char = len(business_reg_num) - 4
    last_char = len(business_reg_num)
    return f'{"".join(business_name.split())}+{business_reg_num[first_char:last_char]}+unyte.com'
