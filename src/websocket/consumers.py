from channels.generic.websocket import AsyncJsonWebsocketConsumer

from websocket.utils.keys import user_group_name
from websocket.utils.user_status_cache import set_user_status


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

        self.group_name = user_group_name(self.user.pk)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        set_user_status(self.user.pk, True)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        set_user_status(self.user.pk, False)

    async def receive_json(self, content: dict):
        action = content.get("action")
        if action == "ping":
            await self.send_json({"type": "pong"})
        elif action == "echo":
            message = content.get("message", "")
            await self.send_json({"type": "echo", "message": message})
        elif action == "subscribe":
            topic = content.get("topic")
            if topic:
                await self.channel_layer.group_add(topic, self.channel_name)
                await self.send_json({"type": "subscribed", "topic": topic})
        elif action == "unsubscribe":
            topic = content.get("topic")
            if topic:
                await self.channel_layer.group_discard(topic, self.channel_name)
                await self.send_json({"type": "unsubscribed", "topic": topic})

    async def event_stream_broadcast(self, event: dict):
        await self.send_json(event.get("payload", {}))
