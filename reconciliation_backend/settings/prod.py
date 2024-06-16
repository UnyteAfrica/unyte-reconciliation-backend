# prod.py

from dotenv import load_dotenv, find_dotenv
from .base import *
import os

load_dotenv(find_dotenv())

DEBUG = False
ALLOWED_HOSTS = ['0.0.0.0', 'localhost', '127.0.0.1', 'unyte-reconciliation-backend-dev-ynoamqpukq-uc.a.run.app']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_NAME'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

STATIC_ROOT = BASE_DIR / 'staticfiles'
