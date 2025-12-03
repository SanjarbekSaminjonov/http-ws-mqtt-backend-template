from django.core.cache import cache
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]

        print(self.user)

        if not self.user.is_authenticated:
            await self.close()

        self.user_group_name = f"user_{self.user.pk}"

        await self.channel_layer.group_add(self.user_group_name, self.channel_name)
        cache.set(f"user_{self.user.pk}_online", True)
        await self.accept()

    async def disconnect(self, close_code):
        cache.delete(f"user_{self.user.pk}_online")
        await self.channel_layer.group_discard(self.user_group_name, self.channel_name)

    async def receive_json(self, data):
        message = data["message"]

        action = data["action"]

        if action == "send_message":
            print(message)

        await self.send_message(
            self.user_group_name,
            {
                "type": "chat_message",
                "message": message,
            },
        )

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
