import os
from pprint import pprint

import requests as r
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

SWAGGER_MODULE_NAME = 'Superpool Proxy'
SUPERPOOL_BACKEND_URL = os.getenv('SUPERPOOL_BACKEND_URL')
SUPERPOOL_API_KEY = os.getenv('SUPERPOOL_API_KEY')


class SuperpoolClient:
    def __init__(self) -> None:
        self.headers = {
            'HTTP_X_BACKEND_API_KEY': SUPERPOOL_API_KEY
        }

    def get_all_products(self, **kwargs) -> dict:
        endpoint = kwargs.get('products', 'dashboard/products')
        url = f"{SUPERPOOL_BACKEND_URL}/{endpoint}"
        response = r.get(url, headers=self.headers)  # noqa: S113
        if response.status_code == 500:
            return {
                'status_code': response.status_code,
                'error': 'Server error from Superpool'
            }
        return {'status_code': 200, 'data': response.json()}

    def get_all_products_for_one_merchant(self, merchant_id) -> dict:
        endpoint = f'dashboard/merchants/{merchant_id}/products'
        url = f'{SUPERPOOL_BACKEND_URL}/{endpoint}'
        response = r.get(url, headers=self.headers)  # noqa: S113
        if response.status_code == 500:
            return {
                'status_code': response.status_code,
                'error': 'Server error from Superpool'
            }

        return {'status_code': 200, 'data': response.json()}

    def get_all_policies_for_one_merchant(self, merchant_id) -> dict:
        """
        Error 500
        """
        endpoint = f'dashboard/merchants/{merchant_id}/policies'
        url = f'{SUPERPOOL_BACKEND_URL}/{endpoint}'
        response = r.get(url, headers=self.headers)  # noqa: S113
        if response.status_code == 500:
            return {
                'status_code': response.status_code,
                'error': 'Server error from Superpool'
            }

        return {'status_code': 200, 'data': response.json()}

    def get_all_claims_for_one_merchant(self, merchant_id) -> dict:
        endpoint = f'dashboard/merchants/{merchant_id}/claims'
        url = f'{SUPERPOOL_BACKEND_URL}/{endpoint}'
        response = r.get(url, headers=self.headers)  # noqa: S113
        if response.status_code == 500:
            return {
                'status_code': response.status_code,
                'error': 'Server error from Superpool'
            }

        return {'status_code': 200, 'data': response.json()}

    def get_all_policies_for_one_insurer(self, insurer_id) -> dict:
        endpoint = f'dashboard/insurers/{insurer_id}/policies'
        url = f'{SUPERPOOL_BACKEND_URL}/{endpoint}'

        response = r.get(url, self.headers)  # noqa: S113
        if response.status_code == 500:
            return {
                'status_code': response.status_code,
                'error': 'Server error from Superpool'
            }

        return {'status_code': 200, 'data': response.json()}

    def get_all_claims_for_one_insurer(self, insurer_id) -> dict:
        endpoint = f'dashboard/insurers/{insurer_id}/claims'
        url = f'{SUPERPOOL_BACKEND_URL}/{endpoint}'
        response = r.get(url, headers=self.headers)  # noqa: S113

        if response.status_code == 500:
            return {
                'status_code': response.status_code,
                'error': 'Server error from Superpool'
            }

        return {'status_code': 200, 'data': response.json()}

    def get_all_products_for_one_insurer(self, insurer_id) -> dict:
        endpoint = f'dashboard/insurers/{insurer_id}/products'
        url = f'{SUPERPOOL_BACKEND_URL}/{endpoint}'
        response = r.get(url, headers=self.headers)  # noqa: S113

        if response.status_code == 500:
            return {
                'status_code': response.status_code,
                'error': 'Server error from Superpool'
            }

        return {'status_code': 200, 'data': response.json()}

    def get_travel_quote(self, customer_metadata: dict, insurance_details: dict, coverage_preferences: dict) -> dict:
        endpoint = 'quotes'
        url = f'{SUPERPOOL_BACKEND_URL}/{endpoint}'
        payload = {
            'customer_metadata': customer_metadata,
            'insurance_details': insurance_details,
            'coverage_preferences': coverage_preferences
        }

        response = r.post(url, json=payload, headers=self.headers)  # noqa: S113
        if response.status_code == 500:
            return {
                'status_code': response.status_code,
                'error': 'Server error from Superpool'
            }
        if response.status_code != 200:  # noqa: RET503, RUF100
            return {
                'status_code': response.status_code,
                'error': response.json()
            }
        return {'status_code': 200, 'data': response.json()}

    def get_motor_quote(self, customer_metadata: dict, insurance_details: dict, coverage_preferences: dict) -> dict:
        endpoint = 'quotes'
        url = f'{SUPERPOOL_BACKEND_URL}/{endpoint}'
        payload = {
            'customer_metadata': customer_metadata,
            'insurance_details': insurance_details,
            'coverage_preferences': coverage_preferences
        }

        response = r.post(url, json=payload, headers=self.headers)  # noqa: S113
        if response.status_code == 500:
            return {
                'status_code': response.status_code,
                'error': 'Server error from Superpool'
            }
        if response.status_code != 200:  # noqa: RET503, RUF100
            return {
                'status_code': response.status_code,
                'error': response.json()
            }
        return {'status_code': 200, 'data': response.json()}

    def get_device_quote(self, customer_metadata: dict, insurance_details: dict, coverage_preferences: dict) -> dict:
        endpoint = 'quotes'
        url = f'{SUPERPOOL_BACKEND_URL}/{endpoint}'
        payload = {
            'customer_metadata': customer_metadata,
            'insurance_details': insurance_details,
            'coverage_preferences': coverage_preferences
        }

        response = r.post(url, json=payload, headers=self.headers)  # noqa: S113
        if response.status_code == 500:
            return {
                'status_code': response.status_code,
                'error': 'Server error from Superpool'
            }
        if response.status_code != 200:  # noqa: RET503, RUF100
            return {
                'status_code': response.status_code,
                'error': response.json()
            }
        return {'status_code': 200, 'data': response.json()}


def main() -> None:
    superpool_handler = SuperpoolClient()

    customer_metadata = {
        "first_name": "Chukwuemeka",
        "last_name": "Okoro",
        "email": "chukwuemeka.okoro@example.com",
        "phone": "08012345678",
        "residential_address": {
        "house_number": "12",
        "street": "Adeola Odeku Street",
        "city": "Lagos",
        "state": "Lagos",
        "postal_code": "101241",
        "country": "Nigeria"
        },
        "date_of_birth": "1985-03-25",
        "customer_gender": "M",
        "occupation": "Civil Engineer",
        "identity_card_img": "https://www.example.com/back",
        "utility_bill_img": "https://www.example.com/back",
        "identity_card_type": "driver_license",
        "identity_card_number": "ARES0n0Fzews",
        "identity_card_expiry_date": "2028-06-15"
    }
    insurance_details = {
        "product_type": "Travel",
        "additional_information": {
        "user_age": 34,
        "departure_date": "2024-11-01",
        "return_date": "2024-11-15",
        "insurance_options": "EUROPE SCHENGEN",
        "destination": "France",
        "international_flight": True
        }
    }
    coverage_preferences = {}
    quotes = superpool_handler.get_quote(customer_metadata, insurance_details=insurance_details, coverage_preferences=coverage_preferences)
    available_quotes = quotes.get('data').get('data')
    heirs = 'Heirs Insurance Group'
    heirs_quotes = []

    for company_quotes in available_quotes:
        if company_quotes.get('provider') == heirs:
            heirs_quotes.append(company_quotes)  # noqa: PERF401

    pprint(heirs_quotes)  # noqa: T203

if __name__ == '__main__':
    main()
