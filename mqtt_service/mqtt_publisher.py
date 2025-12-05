"""
MQTT Publisher Interface - Publish messages to MQTT broker via queue
Similar to WebSocket sender pattern for consistency
"""

import logging
import json
from typing import Any

from django.core.cache import cache

logger = logging.getLogger(__name__)

# Import QUEUE_KEY from publisher client
from mqtt_service.publisher_client import MQTTPublisherClient


class MQTTPublisherInterface:
    """Interface for publishing MQTT messages from Django via Redis queue"""

    QUEUE_KEY = MQTTPublisherClient.QUEUE_KEY

    def publish(
        self, topic: str, payload: Any, qos: int = 0, retain: bool = False
    ) -> bool:
        """
        Queue MQTT message for publishing (sync context)

        Args:
            topic: MQTT topic
            payload: Message payload (str, dict, list)
            qos: Quality of Service level (0, 1, 2)
            retain: Whether to retain the message

        Returns:
            bool: True if queued successfully

        Usage:
            from mqtt_service.mqtt_publisher import mqtt_publisher
            mqtt_publisher.publish("device/001/cmd", {"action": "start"}, qos=1)
        """
        try:
            if isinstance(payload, (dict, list)):
                payload = json.dumps(payload)

            message = {
                "topic": topic,
                "payload": str(payload),
                "qos": qos,
                "retain": retain,
            }

            cache.client.get_client().rpush(self.QUEUE_KEY, json.dumps(message))
            logger.debug(f"Queued MQTT publish: {topic}")
            return True

        except Exception as e:
            logger.error(f"Failed to queue MQTT publish: {e}", exc_info=True)
            return False

    async def publish_async(
        self, topic: str, payload: Any, qos: int = 0, retain: bool = False
    ) -> bool:
        """
        Queue MQTT message for publishing (async context)

        Usage:
            from mqtt_service.mqtt_publisher import mqtt_publisher
            await mqtt_publisher.publish_async("device/001/cmd", {"action": "start"})
        """
        return self.publish(topic, payload, qos, retain)


# Singleton instance
mqtt_publisher = MQTTPublisherInterface()
