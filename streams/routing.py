from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(
        r"^v1/streams/(?P<call_sid>[^/]+)/$", consumers.AudioStreamConsumer.as_asgi()
    ),
]
