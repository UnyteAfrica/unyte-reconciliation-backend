# base.py

import os
from pathlib import Path
from datetime import timedelta

from google.cloud import storage
from google.oauth2 import service_account

from django.conf import settings

settings.configure()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = 'django-insecure-0je%(k1gz3_@+ciu1q7a=gq4&q(l2x3w+%7dwq!w+m&0bzbe_z'
DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_yasg',
    'user',
    'insurer',
    'agents',
    'merchants',
    'django_extensions',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = False

CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://0.0.0.0:8080',
    'http://localhost:3004',
    'https://unyte-reconciliation-backend-dev-ynoamqpukq-uc.a.run.app',
    'https://unyte-reconciliations-frontend-dev-ynoamqpukq-uc.a.run.app',
]

CORS_ORIGIN_WHITELIST = [
    'localhost',
    'https://unyte-reconciliation-backend-dev-ynoamqpukq-uc.a.run.app',
    'https://unyte-reconciliations-frontend-dev-ynoamqpukq-uc.a.run.app',
    'http://localhost:3004',
]

CORS_ALLOW_METHODS = (
    'GET',
    'PATCH',
    'POST',
    'PUT',
)

CORS_ALLOW_HEADERS = (
    'accept',
    'authorization',
    'content-type',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
)

SWAGGER_SETTINGS = {
    'SHOW_REQUEST_HEADERS': True,
    'SECURITY_DEFINITIONS': {'Bearer': {'type': 'apiKey', 'name': 'Authorization', 'in': 'header', 'realm': 'api'}},
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': ['get', 'post', 'put', 'delete', 'patch'],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_simplejwt.authentication.JWTAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

ROOT_URLCONF = 'reconciliation_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'reconciliation_backend.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'

GS_BUCKET_NAME = 'reconciliations-dashboard'
STATIC_URL = 'https://storage.googleapis.com/reconciliations-dashboard/static/'

# Read the environment variable for the credentials file path
credentials_file_path = os.getenv('GS_CREDENTIALS_PATH')

if not credentials_file_path:
    credentials_file_path = os.environ.setdefault(
        'GS_CREDENTIALS_PATH', 'gs://reconciliations-dashboard/new-.json-sa.json'
    )

# Download the service account file from GCS if it's a GCS URL
if credentials_file_path.startswith('gs://'):
    bucket_name, blob_name = credentials_file_path.replace('gs://', '').split('/', 1)

    # Define the temporary local file path
    local_temp_file_path = Path('/tmp/service_account.json').resolve()

    storage_client = storage.Client(project='unyte-project')

    # Download the service account file from GCS
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(local_temp_file_path)

    # Use the downloaded service account file to create credentials
    GS_CREDENTIALS = service_account.Credentials.from_service_account_file(local_temp_file_path)

    # Optionally, you can delete the temporary file after creating the credentials
    local_temp_file_path.unlink()
else:
    # Use the credentials file directly if it's a local path
    GS_CREDENTIALS = service_account.Credentials.from_service_account_file(credentials_file_path)

# GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
#     os.path.join(BASE_DIR, 'unyte-project-b1cf8568d4c2.json')
# )


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

STATIC_ROOT = BASE_DIR / 'staticfiles'
AUTH_USER_MODEL = 'user.CustomUser'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = False
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
TO_EMAIL = os.getenv('TO_EMAIL')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_USE_SSL = True
