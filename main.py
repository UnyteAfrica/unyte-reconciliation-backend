import os
import sys
import logging
import django
import psycopg2
from faker import Faker
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

logger = logging.getLogger(__name__)
logger.info("Loader is up and grateful...")

faker = Faker()


# def use_django_models_for_data_creation(env: str, count: int) -> dict[str]:
#     logger.info(f"Inserting fake values into the Insurers table in {env}")
#     for _ in range(count + 1):
#         business_name = faker.company()
#         email = faker.email()
#         admin_name = faker.first_name()
#         business_registration_number = faker.numerify("##########")
#         password = 'testing321'
#         insure_uuid = generate_unyte_unique_insurer_id(business_name, business_registration_number)
#
#         try:
#             Insurer.objects.create(
#                 business_name=business_name,
#                 admin_name=admin_name,
#                 email=email,
#                 password=password,
#                 business_registration_number=business_registration_number,
#                 unyte_unique_insurer_id=insure_uuid,
#             )
#             logger.info("Done!")
#             logger.info(f"{count} number of insurers have been loaded successfully into the DB")
#             return {
#                 "statusCode": "200",
#                 "message": "OK"
#             }
#
#         except Exception as e:
#             return {
#                 "statusCode": "400",
#                 "error": f"{e}"
#             }

def db_connect_env(last_cli_arg: list[str]) -> dict[str | psycopg2.extensions.connection] | str:
    value = last_cli_arg[-1][2:]

    if value == "dev":
        with psycopg2.connect(
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                port=os.getenv('DB_PORT'),
                host=os.getenv("DB_HOST")
        ) as connection:
            return {"connection": connection, "env": value}
    elif value == 'prod':
        with psycopg2.connect(
                database=os.getenv("POSTGRES_NAME"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                port=os.getenv('DB_PORT'),
                host=os.getenv("POSTGRES_HOST")
        ) as connection:
            return {"connection": connection, "env": value}
    else:
        return f"Invalid sys arg: {value}"


def populate_insurers(env: str, count: int, connection: psycopg2.extensions.connection) -> dict[str | str]:
    logger.info(f"Inserting fake values into the Insurers table in {env}")

    business_name = faker.company()
    customer_id = faker.numerify("#")
    admin_name = faker.first_name()
    business_registration_number = faker.numerify("##########")
    insure_uuid = generate_unyte_unique_insurer_id(business_name, business_registration_number)

    for _ in range(count + 1):
        logger.info(f"Inserting row {count}...")
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO insurer_insurer (business_name, customuser_ptr_id, admin_name, "
            "business_registration_number, unyte_unique_insurer_id)"
            "VALUES (%s, %s, %s, %s, %s)",
            (business_name, count, admin_name, business_registration_number, insure_uuid)
        )
    logger.info("Done!")
    return {
        "message": f"{count} number of insurers have been loaded successfully into the DB"
    }


def populate_agents(env: str, count: int, connection: psycopg2.extensions.connection) -> dict[str | str]:
    logger.info(f"Inserting fake values into the agents table for {env}")

    for _ in range(count + 1):
        connection.execute(
            "INSERT INTO insurer_insurer (home_address, email, password, bvn, bank_account, affiliated_company)"
            "VALUES (%s, %s)",
            (faker.address(), faker.email(), "testing321", faker.numerify("###########"), faker.numerify("##########"))
        )
    return {
        "message": f"{count} number of agents have been loaded successfully into the DB"
    }


def main():
    entry_point = db_connect_env(sys.argv)
    conn = entry_point.get('connection')
    env = entry_point.get('env')
    # use_django_models_for_data_creation(env, 20)


if __name__ == "__main__":
    main()
