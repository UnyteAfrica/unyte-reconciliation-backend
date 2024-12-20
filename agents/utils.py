import os
from datetime import datetime

import pyotp
import requests as r
from dotenv import find_dotenv, load_dotenv

from django.forms import ValidationError
from django.utils import timezone

from rest_framework.exceptions import APIException

load_dotenv(find_dotenv())


FRONTED_URL = os.getenv('FRONTEND_URL', 'unyte-reconciliations-frontend-dev-ynoamqpukq-uc.a.run.app')
SUPERPOOL_BACKEND_URL = os.getenv('SUPERPOOL_BACKEND_URL')
SUPERPOOL_API_KEY = os.getenv('SUPERPOOL_API_KEY')


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


def create_merchant_on_superpool(validated_data: dict) -> dict:
        """
        Create merchants on Superpool
        """
        company_name = validated_data.get('company_name')
        business_email = validated_data.get('business_email')
        support_email = validated_data.get('support_email')
        endpoint = 'merchants/'
        url = f'{SUPERPOOL_BACKEND_URL}/{endpoint}'
        response = r.post(  # noqa: S113
            url=url,
            data={
                'company_name': company_name,
                'business_email': business_email,
                'support_email': support_email
            },
            headers={
                'HTTP_X_BACKEND_API_KEY': SUPERPOOL_API_KEY
            }
        )

        if response.status_code != 201:
            return {
                "status_code": response.status_code,
                "error": response.json()
            }
        return {
            "status_code": response.status_code,
            "result": response.json()
        }

def add_string_to_all_fields_in_travel_serializer(data):
    data['customer_metadata']['first_name'] = "string"
    data['customer_metadata']['last_name'] = "string"
    data['customer_metadata']['phone'] = "string"
    data['customer_metadata']['email'] = "string"
    data['customer_metadata']['residential_address']['house_number'] = "string"
    data['customer_metadata']['residential_address']['street'] = "string"
    data['customer_metadata']['residential_address']['city'] = "string"
    data['customer_metadata']['residential_address']['state'] = "string"
    data['customer_metadata']['residential_address']['postal_code'] = "string"
    data['customer_metadata']['residential_address']['country'] = "string"
    data['customer_metadata']['date_of_birth'] = "string"
    data['customer_metadata']['customer_gender'] = "string"
    data['customer_metadata']['occupation'] = "string"
    data['customer_metadata']['identity_card_img'] = "string"
    data['customer_metadata']['utility_bill_img'] = "string"
    data['customer_metadata']['identity_card_type'] = "string"
    data['customer_metadata']['identity_card_number'] = "string"
    data['customer_metadata']['identity_card_expiry_date'] = "date"
    data['insurance_details']['user_age'] = "number"
    data['insurance_details']['product_type'] = "string"
    data['insurance_details']['additional_information']['departure_date'] = "date"
    data['insurance_details']['additional_information']['return_date'] = "date"
    data['insurance_details']['additional_information']['insurance_options'] = "string"
    data['insurance_details']['additional_information']['destination'] = "string"
    data['insurance_details']['additional_information']['international_flight'] = "boolean"

    return data
