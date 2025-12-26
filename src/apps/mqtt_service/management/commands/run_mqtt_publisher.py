"""
Django management command to run MQTT Publisher service
Usage: python manage.py run_mqtt_publisher [--publisher-id PUBLISHER_ID]
"""

import asyncio
import logging
import os
from django.core.management.base import BaseCommand

from apps.mqtt_service.publisher_client import MQTTPublisherClient

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run MQTT Publisher service"

    def add_arguments(self, parser):
        parser.add_argument(
            "--publisher-id",
            type=str,
            default=os.environ.get("MQTT_PUBLISHER_ID", "publisher_1"),
            help="Unique identifier for this publisher instance (default: publisher_1)",
        )

    def handle(self, *args, **options):
        publisher_id = options["publisher_id"]

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        self.stdout.write(
            self.style.SUCCESS(f"Starting MQTT Publisher: {publisher_id}")
        )

        try:
            publisher = MQTTPublisherClient(publisher_id=publisher_id)
            asyncio.run(publisher.run())
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING(f"MQTT Publisher {publisher_id} stopped by user")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"MQTT Publisher {publisher_id} crashed: {e}")
            )
