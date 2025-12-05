from channels.generic.websocket import AsyncJsonWebsocketConsumer

from utils.user_status_cache import is_user_online, set_user_status


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

    @staticmethod
    def user_group_name(user_id):
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
        ...

    async def mqtt_message(self, event):
        """Handler for MQTT messages from Channel Layer"""
        owner_id = 1  # TODO: Fetch device owner ID from DB if needed
        if is_user_online(owner_id):
            await self.send_message(self.user_group_name(owner_id), event)

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
