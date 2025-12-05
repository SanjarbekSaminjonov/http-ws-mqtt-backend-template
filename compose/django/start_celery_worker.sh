#!/bin/bash

set -o errexit
set -o nounset

echo "Starting Celery Worker..."
celery -A config worker -l INFO --concurrency=2
