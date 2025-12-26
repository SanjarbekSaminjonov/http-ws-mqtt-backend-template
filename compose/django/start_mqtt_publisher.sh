#!/bin/bash

set -o errexit
set -o nounset

echo "Starting MQTT Publisher"
python manage.py run_mqtt_publisher
