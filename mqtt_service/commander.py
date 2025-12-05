"""
MQTT Commander - Publish messages from Django
"""

import logging
import json
from typing import Any

import aiomqtt
from django.conf import settings

logger = logging.getLogger(__name__)


class MQTTCommander:
    """Publish MQTT messages from Django"""

    def __init__(self):
        self.broker_host = settings.MQTT_BROKER_HOST
        self.broker_port = settings.MQTT_BROKER_PORT
        self.username = settings.MQTT_USERNAME or None
        self.password = settings.MQTT_PASSWORD or None

    async def publish(self, topic: str, payload: Any, qos: int = 0) -> bool:
        """Publish message to MQTT broker"""
        try:
            if isinstance(payload, (dict, list)):
                payload = json.dumps(payload)

            async with aiomqtt.Client(
                hostname=self.broker_host,
                port=self.broker_port,
                username=self.username,
                password=self.password,
            ) as client:
                await client.publish(topic, str(payload), qos=qos)
                logger.info(f"Published: {topic}")
                return True

        except Exception as e:
            logger.error(f"Publish error: {e}")
            return False


# Sync wrapper for Django views
def publish_mqtt_message(topic: str, payload: Any, qos: int = 0) -> bool:
    """
    Publish MQTT message (sync)

    Usage:
        from mqtt_service.commander import publish_mqtt_message
        publish_mqtt_message("device/001/cmd", {"action": "start"})
    """
    from asgiref.sync import async_to_sync

    commander = MQTTCommander()
    return async_to_sync(commander.publish)(topic, payload, qos)


# Async wrapper for Django views
async def publish_mqtt_message_async(topic: str, payload: Any, qos: int = 0) -> bool:
    """
    Publish MQTT message (async)

    Usage:
        from mqtt_service.commander import publish_mqtt_message_async
        await publish_mqtt_message_async("device/001/cmd", {"action": "start"})
    """
    commander = MQTTCommander()
    return await commander.publish(topic, payload, qos)
