#!/bin/bash

set -o errexit
set -o nounset

# Get worker number from argument (default: 1)
WORKER_NUM=${1:-1}

echo "Starting MQTT Handler - Worker worker_${WORKER_NUM}"
python manage.py run_mqtt_service --worker-id worker_${WORKER_NUM}
