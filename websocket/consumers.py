from channels.generic.websocket import AsyncJsonWebsocketConsumer

from utils.user_status_cache import set_user_status


class ManagementConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for managing devices
    ws://localhost:8000/ws/connect/
    """

    async def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        self.group_name = self.user_group_name(self.user.pk)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        set_user_status(self.user.pk, True)
        await self.accept()

    def user_group_name(self, user_id):
        return f"user_{user_id}"

    async def disconnect(self, close_code):
        set_user_status(self.user.pk, False)
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content: dict):
        """Handle client messages"""
        action = content.get("action")
        if action == "ping":
            await self.send_json({"type": "pong"})
        elif action == "echo":
            message = content.get("message", "")
            await self.send_json({"type": "echo", "message": message})
        # Add more action handlers here

    async def mqtt_message(self, event):
        """Handler for MQTT messages from Channel Layer"""
        await self.send_json(event)

    async def send_message(self, group_name, message):
        await self.channel_layer.group_send(
            group_name,
            {
                "type": "event.stream.broadcast",
                "payload": message,
            },
        )

    async def event_stream_broadcast(self, event: dict):
        await self.send_json(event.get("payload", {}))
