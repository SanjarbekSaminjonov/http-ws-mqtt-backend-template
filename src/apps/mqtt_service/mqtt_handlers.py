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

        except Exception as e:
            logger.error(
                f"Error handling '{topic = }, {message = }': {e}",
                exc_info=True,
            )
