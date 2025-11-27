#!/bin/sh
# Entrypoint for the clubs microservice

set -e

echo "Using Django settings: ${DJANGO_SETTINGS_MODULE:-clubs_service.settings}" 

python manage.py makemigrations --noinput
python manage.py migrate --noinput

if [ -f seed_data.json ]; then
  python manage.py loaddata seed_data.json || true
fi

python manage.py runserver 0.0.0.0:8000
