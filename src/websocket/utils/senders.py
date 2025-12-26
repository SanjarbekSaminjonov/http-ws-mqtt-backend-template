"""
Helpers to push messages to WebSocket users/groups from any part of Django (views, Celery, MQTT handler).
"""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from websocket.utils.keys import user_group_name


class WebsocketSender:
    """Utility class to send messages to WebSocket groups/users."""

    def __init__(self):
        self.channel_layer = get_channel_layer()

    # -------- sync API --------
    def send_to_user(self, user_id: int, payload: dict) -> None:
        async_to_sync(self.channel_layer.group_send)(
            user_group_name(user_id),
            {"type": "event.stream.broadcast", "payload": payload},
        )

    def send_to_users(self, ids: list[int], payload: dict) -> None:
        for user_id in ids:
            self.send_to_user(user_id, payload)

    def send_to_group(self, group_name: str, payload: dict) -> None:
        async_to_sync(self.channel_layer.group_send)(
            group_name,
            {"type": "event.stream.broadcast", "payload": payload},
        )

    # -------- async API --------
    async def async_send_to_user(self, user_id: int, payload: dict) -> None:
        await self.channel_layer.group_send(
            user_group_name(user_id),
            {"type": "event.stream.broadcast", "payload": payload},
        )

    async def async_send_to_users(self, ids: list[int], payload: dict) -> None:
        for user_id in ids:
            await self.async_send_to_user(user_id, payload)

    async def async_send_to_group(self, group_name: str, payload: dict) -> None:
        await self.channel_layer.group_send(
            group_name,
            {"type": "event.stream.broadcast", "payload": payload},
        )


# Singleton instance
websocket_sender = WebsocketSender()
