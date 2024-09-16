import json
import logging
import sys

from main import RandomDataDBLoader
from gcloud import storage
import os

current_dir = os.getcwd()
credentials_path = os.path.join(current_dir, 'unyte-project-b1cf8568d4c2.json')

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

logging.basicConfig(
    level=logging.INFO,
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    handlers=[
        logging.StreamHandler()
    ]
)


class GCPLoader:

    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.client = storage.Client(project='unyte-project')
        self.bucket_names: list = []

    def _check_bucket_exists_and_update_bucket_lists(self):
        try:
            bucket_name_list: list = [bucket.name for bucket in self.client.list_buckets()]
            self.bucket_names = bucket_name_list
            if self.bucket_name not in bucket_name_list:
                return 400
            return 200
        except Exception as e:
            return e.__str__()

    def get_all_files_from_buckets(self, bucket_name):
        exists: int = self._check_bucket_exists_and_update_bucket_lists()
        if exists != 200:
            return exists
        pass

    def load_insurance_product_and_product_type(self, db_loader: RandomDataDBLoader, insurance_company: str,
                                                insurance_email: str):
        exists: int = self._check_bucket_exists_and_update_bucket_lists()
        if exists != 200:
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
                    logging.info(f"Not processing policies from {insurer_name} currently")
                    pass
                if insurer_name != insurance_company:
                    logging.info(f"Not processing policies from {insurer_name} currently")
                    pass
                elif insurer_policy != 'policies':
                    logging.info(f"Not processing {insurer_policy} from {insurer_name}")
                    pass
                else:
                    logging.info(
                        f"Currently processing {len(policies)} policies in {insurer_policy_name} from insurer: {insurer_name}")
                    db_loader.create_arbitrary_products_for_insurer(insurance_email, policies)
                    db_loader.create_arbitrary_product_types_for_all_products_for_insurer(insurance_email, policies)
            except Exception as e:
                print(e.__str__())

    def validate_load_all_products_for_insurer(self, db_loader: RandomDataDBLoader, insurance_company: str,
                                               insurer_email: str):
        exists: int = self._check_bucket_exists_and_update_bucket_lists()
        total_policies = 0
        if exists != 200:
            return exists
        bucket = self.client.get_bucket(self.bucket_name)
        blobs = bucket.list_blobs()

        for blob in blobs:
            insurer_name = blob.name.split('/')[0]
            insurer_policy = blob.name.split('/')[1]
            try:
                policies = json.loads(blob.download_as_string().decode('utf-8'))
                if insurer_name != insurance_company:
                    pass
                if insurer_name != insurance_company:
                    pass
                elif insurer_policy != 'policies':
                    pass
                else:
                    total_policies += len(policies)
            except Exception as e:
                print(e.__str__())

        all_products_obj_count = db_loader.validate_successful_loading_for_all_products(insurer_email)
        logging.info(f"Total number of product objects count from db: {all_products_obj_count}")
        logging.info(f"Total number of product  loaded JSON: {total_policies}")
        return all_products_obj_count == total_policies

    def validate_load_all_product_types_for_insurer(self, db_loader: RandomDataDBLoader, insurance_company: str,
                                                    insurer_email: str):
        exists: int = self._check_bucket_exists_and_update_bucket_lists()
        total_no_of_product_types = 0
        if exists != 200:
            return exists
        bucket = self.client.get_bucket(self.bucket_name)
        blobs = bucket.list_blobs()

        for blob in blobs:
            insurer_name = blob.name.split('/')[0]
            insurer_policy = blob.name.split('/')[1]
            try:
                policies = json.loads(blob.download_as_string().decode('utf-8'))
                logging.info(policies)
                if insurer_name != insurance_company:
                    pass
                if insurer_name != insurance_company:
                    pass
                elif insurer_policy != 'policies':
                    pass
                else:
                    for policy in policies:
                        total_no_of_product_types += len(policy.get('Premiums'))
            except Exception as e:
                logging.warning(f"{e.__str__()}")
        all_product_types_obj_count = db_loader.validate_successful_loading_for_all_product_types(insurer_email)
        logging.info(f"Total number of product types objects count from db: {all_product_types_obj_count}")
        logging.info(f"Total number of product types loaded JSON: {total_no_of_product_types}")
        return total_no_of_product_types == all_product_types_obj_count


def main():
    pass
    db_loader = RandomDataDBLoader()
    main_loader = GCPLoader('policies-and-quotes')

    insurance_company = sys.argv[len(sys.argv) - 1]
    insurance_email = sys.argv[len(sys.argv) - 2]

    print(main_loader.load_insurance_product_and_product_type(db_loader, insurance_company, insurance_email))
    print(main_loader.validate_load_all_products_for_insurer(db_loader, insurance_company, insurance_email))
    print(main_loader.validate_load_all_product_types_for_insurer(db_loader, insurance_company, insurance_email))



if __name__ == "__main__":
    main()
