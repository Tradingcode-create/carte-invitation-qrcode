from django.urls import path

from .consumers import SupportHubConsumer


websocket_urlpatterns = [
    path("ws/support/", SupportHubConsumer.as_asgi()),
]
