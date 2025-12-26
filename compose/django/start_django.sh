#!/bin/bash

set -o errexit
set -o nounset

if [[ "$DJANGO_DEBUG" = "True" || "$DJANGO_DEBUG" = "true" ]]; then
    echo "Starting Django in DEBUG mode..."
    python manage.py migrate
    python manage.py runserver 0.0.0.0:8000
else
    echo "Starting Django in PRODUCTION mode..."
    python manage.py collectstatic --noinput
    python manage.py migrate
    gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers 3
fi
