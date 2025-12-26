#!/bin/bash

set -o errexit
set -o nounset

echo "Starting Celery Flower..."
celery -A config flower \
    --port=5555 \
    --basic_auth="${FLOWER_USER}:${FLOWER_PASSWORD}"
