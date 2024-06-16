# dev.py

from dotenv import load_dotenv, find_dotenv
from .base import *
import os

load_dotenv(find_dotenv())


DEBUG = True
ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv("DB_NAME"),
        'USER': os.getenv("DB_USER"),
        'PASSWORD': os.getenv("DB_PASSWORD"),
        'HOST': os.getenv("DB_HOST"),
        'PORT': os.getenv("DB_PORT"),
        'TEST': {
            'NAME': 'testdb',

        }
    },
}


