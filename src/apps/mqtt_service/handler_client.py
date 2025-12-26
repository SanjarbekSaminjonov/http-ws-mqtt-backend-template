"""
MQTT Handler Client
Handles connection, subscription, and message processing with shared subscription support
Similar to publisher pattern for consistency
"""

import asyncio
import logging
from typing import Callable, Optional

import aiomqtt
from django.conf import settings

logger = logging.getLogger(__name__)


class MQTTHandlerClient:
    """
    MQTT handler client with shared subscription support for multi-worker setup
    Receives messages from MQTT broker and processes them
    """

    def __init__(
        self,
        message_handler: Callable,
        handler_id: str,
    ):
        """
        Initialize MQTT handler client

        Args:
            message_handler: Async callable to handle received messages
            handler_id: Unique handler identifier for logging
        """
        self.broker_host = settings.MQTT_BROKER_HOST
        self.broker_port = settings.MQTT_BROKER_PORT
        self.username = settings.MQTT_USERNAME
        self.password = settings.MQTT_PASSWORD

        self.message_handler = message_handler
        self.handler_id = handler_id
        self._client: Optional[aiomqtt.Client] = None
        self._reconnect_interval = 5  # seconds

    def create_client(self) -> aiomqtt.Client:
        """
        Create MQTT client instance (not connected yet)

        Returns:
            MQTT client instance
        """
        # Har bir worker unique client_id bilan connect bo'ladi
        # Bu MQTT broker da har bir connection ni alohida ko'rsatadi
        # Lekin shared subscription orqali messages load balanced bo'ladi
        return aiomqtt.Client(
            hostname=self.broker_host,
            port=self.broker_port,
            username=self.username if self.username else None,
            password=self.password if self.password else None,
            identifier=f"handlers-{self.handler_id}",
            keepalive=60,
            clean_session=True,
        )

    async def subscribe_to_topics(self, client: aiomqtt.Client):
        """
        Subscribe to topics with shared subscription for load balancing

        Args:
            client: Connected MQTT client
        """
        for topic in [
            "from_device/+/status",
            "from_device/+/event",
            # Add your topics here
        ]:
            # Shared subscription format: $share/{group_name}/{topic}
            shared_topic = f"$share/handlers/{topic}"
            await client.subscribe(shared_topic, qos=1)
            logger.info(
                f"Handler {self.handler_id}: Subscribed to shared topic: {shared_topic} "
                f"(QoS=1)"
            )

    async def handle_messages(self, client: aiomqtt.Client):
        """
        Listen and process incoming MQTT messages

        Args:
            client: Connected MQTT client
        """
        async for message in client.messages:
            try:
                # Decode message payload
                payload = message.payload.decode()
                topic = str(message.topic)

                # Call message handler if provided
                if self.message_handler:
                    await self.message_handler(topic, payload, message)
                else:
                    logger.info(
                        f"Handler {self.handler_id}: Received message on topic '{topic}': {payload}"
                    )
            except Exception as e:
                logger.error(
                    f"Handler {self.handler_id}: Error processing message: {e}",
                    exc_info=True,
                )

    async def publish(
        self, topic: str, payload: str, qos: int = 1, retain: bool = False
    ):
        """
        Publish message to MQTT broker

        Args:
            topic: Topic to publish to
            payload: Message payload
            qos: Quality of Service level (0, 1, or 2)
            retain: Whether to retain the message
        """
        if not self._client:
            logger.error("Cannot publish: Client not connected")
            return

        try:
            await self._client.publish(topic, payload, qos=qos, retain=retain)
            logger.info(f"Handler {self.handler_id}: Published to '{topic}': {payload}")
        except Exception as e:
            logger.error(
                f"Handler {self.handler_id}: Publish error: {e}", exc_info=True
            )

    async def run(self):
        """
        Main loop with auto-reconnect functionality
        """
        while True:
            try:
                # Create and connect to broker using context manager
                async with self.create_client() as client:
                    self._client = client
                    logger.info(
                        f"Handler {self.handler_id}: Connected to MQTT broker at "
                        f"{self.broker_host}:{self.broker_port}"
                    )

                    # Subscribe to topics
                    await self.subscribe_to_topics(client)

                    # Start listening for messages
                    await self.handle_messages(client)

            except aiomqtt.MqttError as error:
                logger.error(
                    f"Handler {self.handler_id}: MQTT error: {error}. "
                    f"Reconnecting in {self._reconnect_interval} seconds..."
                )
                await asyncio.sleep(self._reconnect_interval)

            except asyncio.CancelledError:
                logger.info(f"Handler {self.handler_id}: MQTT client cancelled")
                break

            except Exception as e:
                logger.error(
                    f"Handler {self.handler_id}: Unexpected error: {e}. "
                    f"Reconnecting in {self._reconnect_interval} seconds...",
                    exc_info=True,
                )
                await asyncio.sleep(self._reconnect_interval)
            finally:
                self._client = None
