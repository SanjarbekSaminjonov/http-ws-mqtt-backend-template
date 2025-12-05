from django.urls import path
from websocket import consumers

websocket_urlpatterns = [
    path("ws/connect/", consumers.ManagementConsumer.as_asgi()),
]
