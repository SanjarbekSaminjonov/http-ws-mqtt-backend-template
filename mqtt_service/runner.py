"""
MQTT Service Runner
Main entry point for running MQTT service
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django

django.setup()

from mqtt_service.client import MQTTClient
from mqtt_service.handlers import MessageHandler

logger = logging.getLogger(__name__)


async def run_mqtt_service(worker_id: str = "worker_1"):
    """
    Run MQTT service with message handler

    Args:
        worker_id: Unique identifier for this worker instance
    """
    logger.info(f"Starting MQTT service worker: {worker_id}")

    # Initialize message handler
    handler = MessageHandler()

    # Initialize MQTT client with handler
    client = MQTTClient(message_handler=handler.handle_message, worker_id=worker_id)

    # Run client (with auto-reconnect)
    await client.run()


def main():
    """
    Main entry point
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Get worker ID from environment or use default
    worker_id = os.environ.get("MQTT_WORKER_ID", "worker_1")

    try:
        # Run async service
        asyncio.run(run_mqtt_service(worker_id))
    except KeyboardInterrupt:
        logger.info(f"MQTT service {worker_id} stopped by user")
    except Exception as e:
        logger.error(f"MQTT service {worker_id} crashed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
