# prod.py

from dotenv import load_dotenv, find_dotenv
from .base import *
import os

load_dotenv(find_dotenv())

DEBUG = False
ALLOWED_HOSTS = ['0.0.0.0', 'localhost', '127.0.0.1', 'unyte-reconciliation-backend-dev-ynoamqpukq-uc.a.run.app']

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SWAGGER_SETTINGS = {
    'SHOW_REQUEST_HEADERS': True,
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'realm': 'api'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
        'put',
        'delete',
        'patch'
    ],
    'DEFAULT_API_URL': 'https://unyte-reconciliation-backend-dev-ynoamqpukq-uc.a.run.app',
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASS'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
        'TEST': {
            'NAME': 'testdb',
        }
    }

}

STATIC_ROOT = BASE_DIR / 'staticfiles'
