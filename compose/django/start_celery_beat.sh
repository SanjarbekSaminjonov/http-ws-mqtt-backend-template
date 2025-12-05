#!/bin/bash

set -o errexit
set -o nounset

echo "Starting Celery Beat..."
celery -A config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
