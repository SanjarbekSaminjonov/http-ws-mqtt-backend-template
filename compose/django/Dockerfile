FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

COPY ./src/requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY ./compose/django/entrypoint.sh /entrypoint
RUN cat /entrypoint | sed 's/\r$//' > /entrypoint
RUN chmod +x /entrypoint

COPY ./compose/django/check_health.sh /check_health
RUN cat /check_health | sed 's/\r$//' > /check_health
RUN chmod +x /check_health

COPY ./compose/django/start_django.sh /start_django
RUN cat /start_django | sed 's/\r$//' > /start_django
RUN chmod +x /start_django

COPY ./compose/django/start_celery_worker.sh /start_celery_worker
RUN cat /start_celery_worker | sed 's/\r$//' > /start_celery_worker
RUN chmod +x /start_celery_worker

COPY ./compose/django/start_celery_beat.sh /start_celery_beat
RUN cat /start_celery_beat | sed 's/\r$//' > /start_celery_beat
RUN chmod +x /start_celery_beat

COPY ./compose/django/start_celery_flower.sh /start_celery_flower
RUN cat /start_celery_flower | sed 's/\r$//' > /start_celery_flower
RUN chmod +x /start_celery_flower

COPY ./compose/django/start_mqtt_handler.sh /start_mqtt_handler
RUN cat /start_mqtt_handler | sed 's/\r$//' > /start_mqtt_handler
RUN chmod +x /start_mqtt_handler

COPY ./compose/django/start_mqtt_publisher.sh /start_mqtt_publisher
RUN cat /start_mqtt_publisher | sed 's/\r$//' > /start_mqtt_publisher
RUN chmod +x /start_mqtt_publisher

# Copy project
COPY ./src /app/
ENTRYPOINT ["/entrypoint"]
