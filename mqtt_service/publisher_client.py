"""
MQTT Publisher Client
Continuously connected to MQTT broker and publishes messages from Redis queue
Similar to handler pattern for consistency
"""

import asyncio
import json
import logging
from typing import Optional

import aiomqtt
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class MQTTPublisherClient:
    """Persistent MQTT publisher client with queue-based publishing"""

    QUEUE_KEY = "mqtt:publish_queue"

    def __init__(self, publisher_id: str = "1"):
        self.publisher_id = publisher_id
        self.broker_host = settings.MQTT_BROKER_HOST
        self.broker_port = settings.MQTT_BROKER_PORT
        self.username = settings.MQTT_USERNAME or None
        self.password = settings.MQTT_PASSWORD or None
        self._client: Optional[aiomqtt.Client] = None
        self._reconnect_interval = 5
        self._running = False

    def create_client(self) -> aiomqtt.Client:
        """Create MQTT client instance"""
        return aiomqtt.Client(
            hostname=self.broker_host,
            port=self.broker_port,
            username=self.username,
            password=self.password,
            identifier=f"publishers-{self.publisher_id}",
            keepalive=60,
            clean_session=True,
        )

    async def publish_from_queue(self, client: aiomqtt.Client):
        """Process messages from Redis queue and publish to MQTT"""
        while self._running:
            try:
                # Get message from Redis queue (blocking with timeout)
                message_data = cache.client.get_client().blpop(
                    self.QUEUE_KEY, timeout=1
                )

                if not message_data:
                    await asyncio.sleep(0.1)
                    continue

                _, message_json = message_data
                message = json.loads(message_json)

                topic = message.get("topic")
                payload = message.get("payload", "")
                qos = message.get("qos", 0)
                retain = message.get("retain", False)

                # Publish to MQTT broker
                await client.publish(topic, str(payload), qos=qos, retain=retain)
                logger.info(f"Publisher-{self.publisher_id}: Published to '{topic}'")

            except json.JSONDecodeError as e:
                logger.error(f"Publisher-{self.publisher_id}: Invalid JSON: {e}")
            except Exception as e:
                logger.error(
                    f"Publisher-{self.publisher_id}: Error processing queue: {e}",
                    exc_info=True,
                )
                await asyncio.sleep(1)

    async def run(self):
        """Main loop with auto-reconnect"""
        self._running = True
        logger.info(f"Publisher-{self.publisher_id}: Starting MQTT Publisher")

        while self._running:
            try:
                async with self.create_client() as client:
                    self._client = client
                    logger.info(
                        f"Publisher-{self.publisher_id}: Connected to MQTT broker at "
                        f"{self.broker_host}:{self.broker_port}"
                    )

                    # Start processing queue
                    await self.publish_from_queue(client)

            except aiomqtt.MqttError as error:
                logger.error(
                    f"Publisher-{self.publisher_id}: MQTT error: {error}. "
                    f"Reconnecting in {self._reconnect_interval}s..."
                )
                await asyncio.sleep(self._reconnect_interval)

            except asyncio.CancelledError:
                logger.info(f"Publisher-{self.publisher_id}: Cancelled")
                self._running = False
                break

            except Exception as e:
                logger.error(
                    f"Publisher-{self.publisher_id}: Unexpected error: {e}. "
                    f"Reconnecting in {self._reconnect_interval}s...",
                    exc_info=True,
                )
                await asyncio.sleep(self._reconnect_interval)
            finally:
                self._client = None

    def stop(self):
        """Stop the publisher"""
        self._running = False
