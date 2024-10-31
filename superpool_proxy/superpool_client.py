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
        endpoint = kwargs.get('products', 'products')
        url = f"{SUPERPOOL_BACKEND_URL}/{endpoint}"
        response = r.get(url, headers=self.headers)  # noqa: S113

        return response.json()

    def get_all_products_one_merchant(self, **kwargs) -> dict:
        merchant_id = kwargs.get('merchant_id')
        endpoint = kwargs.get(f'merchants/{merchant_id}/products', f'merchants/{merchant_id}/products')
        url = f'{SUPERPOOL_BACKEND_URL}/{endpoint}'
        response = r.get(url, headers=self.headers)  # noqa: S113

        return response.json()

    def get_all_policies_one_merchant(self, **kwargs) -> dict:
        merchant_id = kwargs.get('merchant_id')
        endpoint = kwargs.get(f'merchants/{merchant_id}/policies', f'merchants/{merchant_id}/policies')
        url = f'{SUPERPOOL_BACKEND_URL}/{endpoint}'
        response = r.get(url, headers=self.headers)  # noqa: S113

        return response.json()

    def get_all_claims_one_merchant(self, **kwargs) -> dict:
        merchant_id = kwargs.get('merchant_id')
        endpoint = kwargs.get(f'merchants/{merchant_id}/claims', f'merchants/{merchant_id}/claims')
        url = f'{SUPERPOOL_BACKEND_URL}/{endpoint}'
        response = r.get(url, headers=self.headers)  # noqa: S113

        return response.json()

    def get_all_products_one_insurer(self, **kwargs) -> dict:
        insurer_id = kwargs.get('insurer_id')
        endpoint = kwargs.get(f'insurers/{insurer_id}/products', f'insurers/{insurer_id}/products')
        url = f'{SUPERPOOL_BACKEND_URL}/{endpoint}'
        response = r.get(url, headers=self.headers)  # noqa: S113

        return response.json()

    def get_all_policies_one_insurer(self, **kwargs) -> dict:
        insurer_id = kwargs.get('insurer_id')
        endpoint = kwargs.get(f'insurers/{insurer_id}/policies', f'insurers/{insurer_id}/policies')
        url = f'{SUPERPOOL_BACKEND_URL}/{endpoint}'
        response = r.get(url, headers=self.headers)  # noqa: S113

        return response.json()

    def get_all_claims_one_insurer(self, **kwargs) -> dict:
        insurer_id = kwargs.get('insurer_id')
        endpoint = kwargs.get(f'insurers/{insurer_id}/claims', f'insurers/{insurer_id}/claims')
        url = f'{SUPERPOOL_BACKEND_URL}/{endpoint}'
        response = r.get(url, headers=self.headers)  # noqa: S113

        return response.json()

    def get_all_product_types_sold_by_agent_for_one_insurer(self, **kwargs) -> dict:
        insurer_id = kwargs.get('insurer_id')
        endpoint = kwargs.get(f'insurers/{insurer_id}/agents/product-types', f'insurers/{insurer_id}/agents/product-types')
        url = f'{SUPERPOOL_BACKEND_URL}/{endpoint}'
        response = r.get(url, headers=self.headers)  # noqa: S113

        return response.json()

    def get_all_customers_agent_sold_producty_types_for_one_insurer(self, **kwargs) -> dict:
        insurer_id = kwargs.get('insurer_id')
        endpoint = kwargs.get(f'insurers/{insurer_id}/agents/customers', f'insurers/{insurer_id}/agents/customers')
        url = f'{SUPERPOOL_BACKEND_URL}/{endpoint}'
        response = r.get(url, headers=self.headers)  # noqa: S113

        return response.json()

    def get_all_product_sold_by_agent_for_one_insurer(self, **kwargs) -> dict:
        insurer_id = kwargs.get('insurer_id')
        endpoint = kwargs.get(f'insurers/{insurer_id}/agents/products', f'insurers/{insurer_id}/agents/products')
        url = f'{SUPERPOOL_BACKEND_URL}/{endpoint}'
        response = r.get(url, headers=self.headers)  # noqa: S113

        return response.json()