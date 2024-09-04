import datetime
import os
import random
import logging
import sys

import django
import pytz
import requests
from faker import Faker
from dotenv import load_dotenv, find_dotenv
from datetime import date

from agents.utils import generate_unyte_unique_agent_id

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reconciliation_backend.settings.scripts')
django.setup()

from insurer.utils import generate_unyte_unique_insurer_id
from insurer.models import Insurer
from agents.models import Agent
from policies.models import Policies, PolicyProductType, AgentPolicy

load_dotenv(find_dotenv())

faker = Faker()

DEV_URL = 'http://localhost:8000/api/'
PROD_URL = 'https://unyte-reconciliation-backend-dev-ynoamqpukq-uc.a.run.app/api/'

logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG if you want more detailed logs
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    handlers=[
        logging.StreamHandler()  # Sends logging output to console
        # To log to a file, use: logging.FileHandler("app.log")
    ]
)

policy_names = [
    "Comprehensive Protection Plan",
    "SecureShield Insurance",
    "Premier HealthGuard",
    "Silver Lining Coverage",
    "Family Assurance Policy",
    "Global Travel Protector",
    "Essential Life Safety",
    "Ultimate Business Shield",
    "Future Saver Policy",
    "Accident Care Advantage",
    "HomeSafe Insurance",
    "Golden Years Retirement Plan",
    "Smart Student Insurance",
    "Complete Vehicle Coverage",
    "Elite Property Guard",
    "Personal Liability Shield",
    "Prime Income Protector",
    "Wellness Plus Plan",
    "Critical Illness Coverage",
    "Adventure Travel Guard"
]
policy_categories = [
    "LAUNCH",
    "CREDIT LIFE",
    "DEVICE PROTECTION",
    "TRAVEL COVER",
    "HEALTH",
    "MOTOR REGISTRATION",
    "STUDENT PROTECTION",
    "LOGISTICS",
    "CARD PROTECTION"
]

product_type = [
    {
        "type": "Basic",
        "premium": "2000.00",
        "flat_fee": "YES",
        "broker_commission": 20
    },
    {
        "type": "Standard",
        "premium": "3000.00",
        "flat_fee": "NO",
        "broker_commission": 15
    },
    {
        "type": "Premium",
        "premium": "5000.00",
        "flat_fee": "YES",
        "broker_commission": 25
    },
    {
        "type": "Gold",
        "premium": "7000.00",
        "flat_fee": "NO",
        "broker_commission": 18
    },
    {
        "type": "Platinum",
        "premium": "10000.00",
        "flat_fee": "YES",
        "broker_commission": 22
    },
    {
        "type": "Silver",
        "premium": "1500.00",
        "flat_fee": "NO",
        "broker_commission": 10
    },
    {
        "type": "Family",
        "premium": "3500.00",
        "flat_fee": "YES",
        "broker_commission": 12
    },
    {
        "type": "Travel",
        "premium": "2500.00",
        "flat_fee": "NO",
        "broker_commission": 17
    },
    {
        "type": "Student",
        "premium": "1200.00",
        "flat_fee": "YES",
        "broker_commission": 8
    },
    {
        "type": "Executive",
        "premium": "8000.00",
        "flat_fee": "NO",
        "broker_commission": 30
    }
]


def check_env() -> str:
    sys_args: list = sys.argv
    last_val: str = sys_args[-1]
    env_var: str = last_val[2:]

    return env_var


def create_arbitrary_insurers(count: int) -> dict[str]:
    env: str = check_env()
    logging.info(f"Inserting fake values into the Insurers table in {env}")
    try:
        for _ in range(count):
            business_name = faker.unique.company()
            business_registration_number = faker.unique.numerify("########")
            payload = {
                "business_name": business_name,
                "email": faker.unique.email(),
                "admin_name": faker.unique.first_name(),
                "business_registration_number": business_registration_number,
                "password": 'testing321',
                "unyte_unique_insurer_id": generate_unyte_unique_insurer_id(business_name,
                                                                            business_registration_number),
                "insurer_gampID": ""
            }
            if env == 'dev':
                endpoint = 'insurer/sign-up'
                BASE_URL = DEV_URL + endpoint
                response = requests.post(
                    url=BASE_URL,
                    data=payload
                )
                logging.info(response.json())
            elif env == 'prod':
                endpoint = 'insurer/sign-up'
                BASE_URL = PROD_URL + endpoint
                response = requests.post(
                    url=BASE_URL,
                    data=payload
                )
                logging.info(response.json())
            else:
                return {
                    "statusCode": 400,
                    "error": "Invalid env type. Allowed env types [dev, prod]"
                }
        logging.info("Done!")
        logging.info(f"{count} number of insurers have been loaded successfully into the DB")
        return {
            "statusCode": "200",
            "message": "OK"
        }
    except Exception as e:
        return {
            "statusCode": "400",
            "error": f"{e}"
        }


def create_arbitrary_agents(count: int):
    env: str = check_env()
    logging.info(f"Inserting fake values into the agent table in {env}")
    all_insurers = Insurer.objects.all()

    try:
        for _ in range(count):
            home_address = faker.unique.address()
            email = faker.unique.email()
            first_name = faker.unique.first_name()
            last_name = faker.unique.last_name()
            bvn = faker.unique.numerify("###########")
            bank_account = faker.unique.numerify("##########")
            password = 'testing321'
            affiliated_company = random.choice(all_insurers)
            agent_uuid = generate_unyte_unique_agent_id(first_name, bank_account)

            payload = {
                "home_address": home_address,
                "email": email,
                "first_name": first_name,
                "middle_name": "-",
                "last_name": last_name,
                "bvn": bvn,
                "bank_account": bank_account,
                "unyte_unique_agent_id": agent_uuid,
                "password": password,
                "agent_gampID": ""
            }
            endpoint = f'agent/sign-up?invite={affiliated_company.unyte_unique_insurer_id}'
            endpoint = endpoint.replace("+", '%2B')
            if env == 'dev':
                BASE_URL = DEV_URL + endpoint
                response = requests.post(
                    url=BASE_URL,
                    data=payload
                )
                print(response.json())
            elif env == 'prod':
                BASE_URL = PROD_URL + endpoint
                response = requests.post(
                    url=BASE_URL,
                    data=payload
                )
                print(response.json())
            else:
                return {
                    "statusCode": 400,
                    "error": "Invalid env type. Allowed env types [dev, prod]"
                }
        logging.info("Done!")
        logging.info(f"{count} number of agents have been loaded successfully into the DB")
        return {
            "statusCode": "200",
            "message": "OK"
        }
    except Exception as e:
        return {
            "statusCode": "400",
            "error": f"{e}"
        }


def create_arbitrary_products(count: int):
    logging.info(f"Inserting fake values into the policies table in env or prod")
    all_insurers = Insurer.objects.all()

    try:

        for insurer in all_insurers:
            for _ in range(count):
                # tbc -> to be created
                tbc_policy_name = random.choice(policy_names)
                policies = Policies.objects.filter(insurer=insurer)
                all_policy_names = [policy.name for policy in policies]

                if tbc_policy_name in all_policy_names:
                    pass
                else:
                    policy_name = tbc_policy_name
                    policy_category = random.choice(policy_categories)
                    valid_from = faker.date_time_between(
                        start_date=datetime.datetime(2023, 1, 20, 20, 8, 7, tzinfo=pytz.UTC),
                        end_date=datetime.datetime(2023, 9, 20, 20, 8, 7, tzinfo=pytz.UTC))
                    valid_to = faker.date_time_between(
                        start_date=datetime.datetime(2023, 10, 20, 20, 8, 7, tzinfo=pytz.UTC),
                        end_date=datetime.datetime(2023, 11, 20, 20, 8, 7, tzinfo=pytz.UTC))
                    policy = Policies.objects.create(
                        name=policy_name,
                        insurer=insurer,
                        policy_category=policy_category,
                        valid_from=valid_from,
                        valid_to=valid_to
                    )
                    policy.save()
        logging.info("Done!")
        logging.info(f"{count} number of policies have been loaded successfully into the DB")
        return {
            "statusCode": 200,
            "message": "OK"
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "message": e.__str__()
        }


def create_arbitrary_products_for_one_insurer(env: str, count: int, insurer_mail: str):
    logging.info(f"Inserting fake values into the policies table in {env}")
    try:
        insurer = Insurer.objects.get(email=insurer_mail)
        for _ in range(count):
            # tbc -> to be created
            tbc_policy_name = random.choice(policy_names)
            policies = Policies.objects.filter(insurer=insurer)
            all_policy_names = [policy.name for policy in policies]

            if tbc_policy_name in all_policy_names:
                # policy = Policies.objects.get(name=tbc_policy_name)
                print({
                    "message": f"Existing policy with name: {tbc_policy_name}",
                    # "existing_policy_id": f"{policy.id}"
                })
            else:
                policy_category = random.choice(policy_categories)
                valid_from = faker.date_time_between(
                    start_date=datetime.datetime(2023, 1, 20, 20, 8, 7, tzinfo=pytz.UTC))
                valid_to = faker.date_time_between(start_date=datetime.datetime(2023, 2, 20, 20, 8, 7, tzinfo=pytz.UTC))
                policy = Policies.objects.create(
                    name=tbc_policy_name,
                    insurer=insurer,
                    policy_category=policy_category,
                    valid_from=valid_from,
                    valid_to=valid_to
                )
                policy.save()
        logging.info("Done!")
        logging.info(f"{count} number of policies have been loaded successfully into the DB")
        return {
            "statusCode": 200,
            "message": "OK"
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "message": e.__str__()
        }


def create_arbitrary_product_types_for_one_product(env: str, count: int, product_name: str, insurer_email: str):
    logging.info(f"Inserting fake values into the policy_product_type table in {env}")
    try:
        insurer = Insurer.objects.get(email=insurer_email)
        product = Policies.objects.get(name=product_name, insurer=insurer)
        random_product_type = random.choice(product_type)
        for _ in range(count):
            product_with_types = PolicyProductType.objects.create(
                policy=product,
                name=random_product_type.get('type'),
                premium=random_product_type.get('premium'),
                flat_fee=random_product_type.get('flat_fee'),
                broker_commission=random_product_type.get('broker_commission')
            )
            product_with_types.save()
        logging.info("Done!")
        logging.info(
            f"{count} number of product_types have been loaded successfully into the DB and attached to it's product")
        return {
            "statusCode": 200,
            "message": "OK"
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "message": e.__str__()
        }


def create_arbitrary_product_types_for_all_products():
    logging.info(f"Inserting fake values into the policy_product_type table in env or prod \n")
    all_insurers = Insurer.objects.all()

    try:
        for insurer in all_insurers:
            logging.info(
                f"Currently attaching product_types for all products associated with {insurer.business_name} \n")
            products = Policies.objects.filter(insurer=insurer)
            for one_product in products:
                count = 0
                iteration_value = random.randrange(1, 4)
                logging.info(f"Currently attaching product_types for all products associated with {one_product.name}")
                if iteration_value == 0:
                    logging.info("Random iteration value is 3, reset to 3")
                    iteration_value = 3
                for _ in range(iteration_value):
                    random_product_type = random.choice(product_type)
                    product_type_obj = PolicyProductType.objects.create(
                        policy=one_product,
                        name=random_product_type.get('type'),
                        premium=random_product_type.get('premium'),
                        flat_fee=random_product_type.get('flat_fee'),
                        broker_commission=random_product_type.get('broker_commission')
                    )
                    count += 1
                    product_type_obj.save()
                logging.info(f"Done attaching {count} number of products to {one_product.name} \n")
            logging.info(f"Done attaching product_types to all products under {insurer.business_name} \n")
        return {
            "statusCode": 200,
            "message": "Completed loading arbitrary product_types to all products for all insurers"
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "error": e.__str__()
        }


def agent_sell_policies():
    all_insurers = Insurer.objects.all()

    # try:
    for insurer in all_insurers:
        print(insurer)
        insurer_product = Policies.objects.filter(insurer=insurer)
        all_agent_obj = Agent.objects.filter(affiliated_company=insurer)

        all_agent_names = [f"{agent.first_name} {agent.last_name}" for agent in all_agent_obj]
        logging.info(f"All agents under insurer: {insurer} are {all_agent_names} \n")

        if len(insurer_product) == 0 or len(all_agent_obj) == 0:
            pass
        else:
            for _ in range(len(insurer_product)):
                random_insurer_product_type_obj = PolicyProductType.objects.filter(
                    policy=random.choice(insurer_product))
                if len(random_insurer_product_type_obj) == 0:
                    pass
                else:
                    for i in range(len(random_insurer_product_type_obj)):
                        random_agent_obj = random.choice(all_agent_obj)
                        agent_sold_policy_obj = AgentPolicy.objects.create(
                            agent=random_agent_obj,
                            product_type=random_insurer_product_type_obj[i],
                            date_sold=faker.date_between(start_date=date(2005, 1, 1), end_date=date(2025, 1, 1))
                        )
                        agent_sold_policy_obj.save()
                        logging.info(
                            f"Agent: {random_agent_obj.first_name} {random_agent_obj.last_name} has sold product type: "
                            f"{random_insurer_product_type_obj[i].name} "
                            f"for product {random_insurer_product_type_obj[i].policy.name}")
        logging.info(f"Done with insurer {insurer.id}")
    #     return {
    #         "statusCode": 200,
    #         "message": "Successfully sold random policy products"
    #     }
    # except Exception as e:
    #     return {
    #         "statusCode": 400,
    #         "error": e.__str__()
    #     }


def main():
    # print(create_arbitrary_insurers(10))
    # print(create_arbitrary_agents(30))

    # print(create_arbitrary_products(100))
    # print(create_arbitrary_product_types_for_all_products())

    print(agent_sell_policies())


if __name__ == "__main__":
    logging.info("Loader is up and grateful...")

    main()
