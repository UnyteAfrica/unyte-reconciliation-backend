#!/bin/bash

# Run initial migrations
python3 manage.py makemigrations

# Run additional migrations
python3 manage.py migrate

# Generate static files for swagger docs
python3 manage.py collectstatic