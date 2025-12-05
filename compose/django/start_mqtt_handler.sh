#!/bin/bash

set -o errexit
set -o nounset

echo "Starting MQTT Handler"
python manage.py run_mqtt_handler
