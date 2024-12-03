import os

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


def main() -> None:
    superpool_handler = SuperpoolClient()

    print(superpool_handler.get_all_products())  # noqa: T201

if __name__ == '__main__':
    main()
