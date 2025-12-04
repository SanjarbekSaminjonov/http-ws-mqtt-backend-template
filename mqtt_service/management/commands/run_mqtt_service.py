"""
Django management command to run MQTT service
Usage: python manage.py run_mqtt_service [--worker-id WORKER_ID]
"""

import asyncio
import logging
import os
from django.core.management.base import BaseCommand

from mqtt_service.client import MQTTClient
from mqtt_service.handlers import MessageHandler

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run MQTT service to handle incoming messages"

    def add_arguments(self, parser):
        parser.add_argument(
            "--worker-id",
            type=str,
            default=os.environ.get("MQTT_WORKER_ID", "worker_1"),
            help="Unique identifier for this worker instance (default: worker_1)",
        )

    def handle(self, *args, **options):
        worker_id = options["worker_id"]

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        self.stdout.write(
            self.style.SUCCESS(f"Starting MQTT service worker: {worker_id}")
        )

        try:
            asyncio.run(self.run_mqtt_service(worker_id))
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING(f"MQTT service {worker_id} stopped by user")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"MQTT service {worker_id} crashed: {e}")
            )
            logger.error(f"MQTT service error: {e}", exc_info=True)
            raise

    async def run_mqtt_service(self, worker_id: str):
        """
        Run MQTT service with message handler

        Args:
            worker_id: Unique identifier for this worker instance
        """
        # Initialize message handler
        handler = MessageHandler()

        # Initialize MQTT client with handler
        client = MQTTClient(message_handler=handler.handle_message, worker_id=worker_id)

        # Run client (with auto-reconnect)
        await client.run()
