"""
WSGI config for reconciliation_backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from dotenv import find_dotenv, load_dotenv

from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.contrib.staticfiles.handlers import StaticFilesHandler

load_dotenv(find_dotenv())


env = os.getenv("ENV")
if env == "dev":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reconciliation_backend.settings.dev")
if env == "staging":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reconciliation_backend.settings.staging")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reconciliation_backend.settings.prod")


# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reconciliation_backend.settings')

# application = get_wsgi_application()

application = get_wsgi_application() if settings.DEBUG else StaticFilesHandler(get_wsgi_application())
