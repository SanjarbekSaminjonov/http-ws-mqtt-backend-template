"""
Message Handlers for MQTT Topics
Process incoming MQTT messages and interact with Django ORM
"""

import json
import logging
from typing import Any
from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


class MessageHandler:
    """
    Handles MQTT messages and integrates with Django ORM
    """

    def __init__(self):
        self.channel_layer = get_channel_layer()

    async def handle_message(self, topic: str, payload: str, message: Any):
        """
        Main message handler that routes to specific handlers based on topic

        Args:
            topic: MQTT topic
            payload: Message payload
            message: Original MQTT message object
        """
        try:
            # Parse JSON payload
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON payload on topic '{topic}': {payload}")
                return

            # Route to specific handlers based on topic pattern
            if "gate/" in topic and "/status" in topic:
                await self.handle_gate_status(topic, data)
            elif "gate/" in topic and "/command" in topic:
                await self.handle_gate_command(topic, data)
            elif "device/" in topic and "/event" in topic:
                await self.handle_device_event(topic, data)
            else:
                logger.warning(f"No handler for topic: {topic}")

        except Exception as e:
            logger.error(
                f"Error handling message from topic '{topic}': {e}", exc_info=True
            )

    async def handle_gate_status(self, topic: str, data: dict):
        """
        Handle gate status updates

        Args:
            topic: MQTT topic (e.g., gate/gate_001/status)
            data: Parsed JSON data
        """
        logger.info(f"Gate status update from {topic}: {data}")

        # Extract gate_id from topic
        parts = topic.split("/")
        if len(parts) >= 2:
            gate_id = parts[1]

            # Django ORM operations must be wrapped with sync_to_async
            # Example: Update gate status in database
            # await self.update_gate_status_db(gate_id, data)

            # Send to WebSocket clients via channels
            if self.channel_layer:
                await self.channel_layer.group_send(
                    f"gate_{gate_id}",
                    {
                        "type": "gate.status",
                        "data": data,
                    },
                )

    async def handle_gate_command(self, topic: str, data: dict):
        """
        Handle gate command messages

        Args:
            topic: MQTT topic (e.g., gate/gate_001/command)
            data: Parsed JSON data
        """
        logger.info(f"Gate command from {topic}: {data}")

        parts = topic.split("/")
        if len(parts) >= 2:
            gate_id = parts[1]

            # Process command
            # await self.process_gate_command_db(gate_id, data)

    async def handle_device_event(self, topic: str, data: dict):
        """
        Handle device event messages

        Args:
            topic: MQTT topic (e.g., device/device_001/event)
            data: Parsed JSON data
        """
        logger.info(f"Device event from {topic}: {data}")

        parts = topic.split("/")
        if len(parts) >= 2:
            device_id = parts[1]

            # Process device event
            # await self.log_device_event_db(device_id, data)

    # Django ORM integration examples
    @sync_to_async
    def update_gate_status_db(self, gate_id: str, data: dict):
        """
        Update gate status in database
        This is an example of how to use Django ORM in async context

        Args:
            gate_id: Gate identifier
            data: Status data
        """
        # Example:
        # from main.models import Gate
        # gate = Gate.objects.get(gate_id=gate_id)
        # gate.status = data.get('status')
        # gate.save()
        pass

    @sync_to_async
    def process_gate_command_db(self, gate_id: str, data: dict):
        """
        Process and log gate command

        Args:
            gate_id: Gate identifier
            data: Command data
        """
        # Example:
        # from main.models import GateCommand
        # GateCommand.objects.create(
        #     gate_id=gate_id,
        #     command=data.get('command'),
        #     params=data
        # )
        pass

    @sync_to_async
    def log_device_event_db(self, device_id: str, data: dict):
        """
        Log device event to database

        Args:
            device_id: Device identifier
            data: Event data
        """
        # Example:
        # from main.models import DeviceEvent
        # DeviceEvent.objects.create(
        #     device_id=device_id,
        #     event_type=data.get('event_type'),
        #     data=data
        # )
        pass
