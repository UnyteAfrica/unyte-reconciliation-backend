import os

import pyotp
from dotenv import load_dotenv, find_dotenv
from datetime import datetime

from rest_framework.exceptions import APIException

load_dotenv(find_dotenv())


def generate_otp() -> str:
    totp = pyotp.TOTP(pyotp.random_base32(), interval=60)
    otp = totp.now()

    return otp


class CustomValidationError(APIException):
    status_code = 400
    default_detail = 'Invalid input.'
    default_code = 'invalid'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = {'error': self.default_detail}
        self.detail = detail


def verify_otp(otp_created_at) -> bool:
    current_time = datetime.now().time()
    today = datetime.now().today()

    otp_created_time_datetime = datetime.combine(today, otp_created_at)
    current_datetime = datetime.combine(today, current_time)

    time_delta = current_datetime - otp_created_time_datetime

    if time_delta.total_seconds() >= 120:
        return False

    return True


def gen_absolute_url(current_site, relative_link, token):
    if os.getenv('ENV') != 'dev':
        return f'https://{current_site}{relative_link}?token={str(token)}'
    return f'http://{current_site}{relative_link}?token={str(token)}'


def gen_sign_up_url_for_agent(frontend_url, relative_link, unyte_unique_insurer_id):
    if os.getenv('ENV') != 'dev':
        return f'https://{frontend_url}{relative_link}?invite={str(unyte_unique_insurer_id)}'
    return f'http://{frontend_url}{relative_link}?invite={str(unyte_unique_insurer_id)}'


def generate_unyte_unique_insurer_id(business_name: str, business_reg_num: str) -> str:
    first_char = len(business_reg_num) - 4
    last_char = len(business_reg_num)
    unyte_unique_insurer_id = f'{"".join(business_name.split())}+{business_reg_num[first_char:last_char]}+unyte.com'
    return unyte_unique_insurer_id
