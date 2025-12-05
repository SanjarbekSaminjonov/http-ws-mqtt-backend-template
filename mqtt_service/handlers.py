"""
MQTT Message Handler
"""

import json
import logging
from typing import Any
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


class MessageHandler:
    """
    MQTT message handler with Django ORM and WebSocket support
    """

    def __init__(self):
        self.channel_layer = get_channel_layer()

    async def handle_message(self, topic: str, payload: str, message: Any):
        """
        Main message handler

        Args:
            topic: MQTT topic
            payload: Message payload
            message: MQTT message object
        """
        try:
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                logger.warning(f"Non-JSON payload on '{topic}': {payload}")
                data = {"raw": payload}

            logger.info(f"MQTT: {topic} -> {data}")

            # TODO: Add your routing logic here

            # Example: Send to WebSocket
            # await self.send_to_websocket(topic, data)

        except Exception as e:
            logger.error(f"Error handling '{topic}': {e}", exc_info=True)

    async def send_to_websocket(self, topic: str, data: dict):
        """Send to WebSocket via Channel Layer"""
        if self.channel_layer:
            await self.channel_layer.group_send(
                "mqtt_updates",
                {"type": "mqtt_message", "topic": topic, "data": data},
            )
