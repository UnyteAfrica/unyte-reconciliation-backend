import os
import sys
import json
import logging
from pathlib import Path

from gcloud import storage

from main import RandomDataDBLoader

current_dir = Path.cwd()
credentials_path = current_dir / 'unyte-project-b1cf8568d4c2.json'

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

logging.basicConfig(
    level=logging.INFO,
    format='{asctime} - {levelname} - {message}',
    style='{',
    datefmt='%Y-%m-%d %H:%M',
    handlers=[logging.StreamHandler()],
)


class GCPLoader:
    def __init__(self, bucket_name: str):
        self.bucket_name: str = bucket_name
        self.client: storage.Client = storage.Client(project='unyte-project')
        self.products: list = []

    def _check_bucket_exists_and_update_bucket_lists(self):
        try:
            bucket_name_list: list = [bucket.name for bucket in self.client.list_buckets()]
            self.bucket_names = bucket_name_list
            if self.bucket_name not in bucket_name_list:
                return 400
            return 200
        except Exception as e:
            return e.__str__()

    def get_all_files_from_buckets(self):
        exists: int = self._check_bucket_exists_and_update_bucket_lists()
        if exists != 200:
            return exists
        return None

    def load_all_products(self, insurance_company: str) -> None | int:
        exists: int = self._check_bucket_exists_and_update_bucket_lists()
        if exists != 200:
            logging.warning(f'Error status code {exists}')
            return exists
        bucket = self.client.get_bucket(self.bucket_name)
        blobs = bucket.list_blobs()
        for blob in blobs:
            insurer_name = blob.name.split('/')[0]
            insurer_policy = blob.name.split('/')[1]
            insurer_policy_name = blob.name.split('/')[-1]

            try:
                policies = json.loads(blob.download_as_string().decode('utf-8'))
                if insurer_name != insurance_company:
                    logging.info(f'Not processing policies from {insurer_name} currently')
                if insurer_name != insurance_company:
                    logging.info(f'Not processing policies from {insurer_name} currently')
                elif insurer_policy != 'policies':
                    logging.info(f'Not processing {insurer_policy} from {insurer_name}')
                else:
                    logging.info(
                        f'Currently processing {len(policies)} policies in {insurer_policy_name} from insurer: {insurer_name}'  # noqa: E501
                    )
                    for policy in policies:
                        self.products.append(policy)

            except Exception as e:
                logging.warning(f'{e}')
        return None

    def load_insurance_product_and_product_type(self, db_loader: RandomDataDBLoader, insurance_email: str) -> None:
        db_loader.create_arbitrary_products_for_insurer(insurance_email, self.products)
        db_loader.create_arbitrary_product_types_for_all_products_for_insurer(insurance_email, self.products)

    def validate_load_all_products_for_insurer(self, db_loader: RandomDataDBLoader, insurer_email: str) -> bool:
        total_product_count = len(self.products)
        all_products_obj_count = db_loader.validate_successful_loading_for_all_products(insurer_email)

        logging.info(f'Total number of product objects count from db: {all_products_obj_count}')
        logging.info(f'Total number of product  loaded JSON: {total_product_count}')

        return all_products_obj_count == total_product_count

    def validate_load_all_product_types_for_insurer(self, db_loader: RandomDataDBLoader, insurer_email: str) -> bool:
        total_no_of_product_types = 0
        for product in self.products:
            total_no_of_product_types += len(product.get('Premiums'))
        all_product_types_obj_count = db_loader.validate_successful_loading_for_all_product_types(insurer_email)

        logging.info(f'Total number of product objects count from db: {all_product_types_obj_count}')
        logging.info(f'Total number of product  loaded JSON: {total_no_of_product_types}')

        return all_product_types_obj_count == total_no_of_product_types


def main():
    db_loader = RandomDataDBLoader()
    main_loader = GCPLoader('policies-and-quotes')

    insurance_company = sys.argv[len(sys.argv) - 1]
    insurance_email = sys.argv[len(sys.argv) - 2]

    main_loader.load_all_products(insurance_company)
    main_loader.load_insurance_product_and_product_type(db_loader, insurance_email)


if __name__ == '__main__':
    main()
