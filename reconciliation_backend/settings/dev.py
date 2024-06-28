# dev.py

from dotenv import load_dotenv, find_dotenv
from .base import *
# from reconciliation_backend.filters import SensitiveDataFilter
import os

load_dotenv(find_dotenv())

DEBUG = True
ALLOWED_HOSTS = ['0.0.0.0', 'localhost']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv("POSTGRES_NAME"),
        'USER': os.getenv("POSTGRES_USER"),
        'PASSWORD': os.getenv("POSTGRES_PASSWORD"),
        'HOST': os.getenv("POSTGRES_HOST"),
        'PORT': os.getenv("DB_PORT"),
        'TEST': {
            'NAME': 'testdb',

        }
    },
}

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'verbose': {
#             'format': '{levelname} {asctime} {module} {message}',
#             'style': '{',
#         },
#         'simple': {
#             'format': '{levelname} {message}',
#             'style': '{',
#         },
#         'filters': {
#             'sensitive_data_filter': {
#                 '()': 'reconciliation_backend.filters.SensitiveDataFilter',
#             },
#         }
#     },
#     'root': {
#         'handlers': ['console'],
#         'level': 'DEBUG',
#     },
#     'handlers': {
#         'file': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': os.path.join(BASE_DIR, 'debug.log'),
#             'formatter': 'verbose',
#         },
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'simple',
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['console', 'file'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#         'django.request': {
#             'handlers': ['file'],
#             'level': 'ERROR',
#             'propagate': False,
#         },
#         'gunicorn.error': {
#             'handlers': ['console', 'file'],
#             'level': 'ERROR',
#             'propagate': True,
#         },
#         'gunicorn.access': {
#             'handlers': ['console', 'file'],
#             'level': 'INFO',
#             'propagate': True,
#         },
#     },
# }

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
