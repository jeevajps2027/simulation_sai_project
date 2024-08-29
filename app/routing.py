from django.urls import re_path
from app.consumers import SerialConsumer

websocket_urlpatterns = [
    re_path(r'ws/comport/$', SerialConsumer.as_asgi()),
]
