#!/bin/bash

set -o errexit
set -o nounset

# Health check for Django app
# Checks /health/ endpoint for quick response

# Check if curl is installed
if ! command -v curl &> /dev/null; then
    echo "Error: curl is not installed. Please install curl to run health checks."
    exit 1
fi

MAX_RETRIES=30
RETRY_INTERVAL=2

echo "Checking Django health..."

for i in $(seq 1 $MAX_RETRIES); do
    if curl -f -s http://localhost:8000/health/ | grep -q "healthy"; then
        echo "Django is healthy!"
        exit 0
    fi
    
    echo "Attempt $i/$MAX_RETRIES failed. Waiting ${RETRY_INTERVAL}s..."
    sleep $RETRY_INTERVAL
done

echo "Django health check failed after $MAX_RETRIES attempts"
exit 1
