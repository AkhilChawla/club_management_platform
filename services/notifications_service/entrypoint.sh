#!/bin/sh
# Entrypoint for the notifications microservice

set -e

echo "Using Django settings: ${DJANGO_SETTINGS_MODULE:-notifications_service.settings}" 

python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Start the Django server in the background
echo "Starting Django server..."
python manage.py runserver 0.0.0.0:8000 &

# Wait for Django to start and RabbitMQ to be ready
echo "Waiting for services to be ready..."
sleep 10

# Start the notification consumer with retry logic
echo "Starting notification consumer..."
python manage.py start_consumer
