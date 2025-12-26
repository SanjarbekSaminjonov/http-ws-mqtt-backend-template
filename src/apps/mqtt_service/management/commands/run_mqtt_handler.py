"""
Django management command to run MQTT handler
Usage: python manage.py run_mqtt_handler [--handler-id HANDLER_ID]
"""

import asyncio
import logging
import os
from django.core.management.base import BaseCommand

from apps.mqtt_service.handler_client import MQTTHandlerClient
from apps.mqtt_service.mqtt_handlers import MessageHandler

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run MQTT handler to process incoming MQTT messages"

    def add_arguments(self, parser):
        parser.add_argument(
            "--handler-id",
            type=str,
            default=os.environ.get("MQTT_HANDLER_ID", "handler_1"),
            help="Unique identifier for this handler instance (default: handler_1)",
        )

    def handle(self, *args, **options):
        handler_id = options["handler_id"]

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        self.stdout.write(self.style.SUCCESS(f"Starting MQTT handler: {handler_id}"))

        try:
            asyncio.run(self.run_mqtt_handler(handler_id))
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING(f"MQTT handler {handler_id} stopped by user")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"MQTT handler {handler_id} crashed: {e}")
            )
            logger.error(f"MQTT handler error: {e}", exc_info=True)
            raise

    async def run_mqtt_handler(self, handler_id: str):
        """
        Run MQTT handler with message processor

        Args:
            handler_id: Unique identifier for this handler instance
        """
        # Initialize message handler
        handler = MessageHandler()

        # Initialize MQTT handler client
        client = MQTTHandlerClient(
            message_handler=handler.handle_message,
            handler_id=handler_id,
        )

        # Run client (with auto-reconnect)
        await client.run()
