"""Tests for streams.consumers."""

import pytest
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.test import override_settings

from streams.routing import websocket_urlpatterns


CALL_SID = "test-call-sid-123"
WEBSOCKET_URL = f"/v1/streams/{CALL_SID}/"

CHANNEL_LAYERS_OVERRIDE = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}


@pytest.fixture()
def application():
    """Return a URLRouter application wrapping the audio stream consumer."""
    return URLRouter(websocket_urlpatterns)


@pytest.fixture()
def communicator(application):
    """Return a WebsocketCommunicator for the audio stream endpoint."""
    return WebsocketCommunicator(application, WEBSOCKET_URL)


@pytest.mark.asyncio()
@override_settings(CHANNEL_LAYERS=CHANNEL_LAYERS_OVERRIDE)
async def test_connect_sends_connected_event(communicator) -> None:
    """connect() sends a connected event with the call SID on WebSocket connection."""
    connected, _ = await communicator.connect()
    assert connected
    response = await communicator.receive_json_from()
    assert response["event"] == "connected"
    assert response["call_sid"] == CALL_SID
    await communicator.disconnect()


@pytest.mark.asyncio()
@override_settings(CHANNEL_LAYERS=CHANNEL_LAYERS_OVERRIDE)
async def test_disconnect_leaves_group(communicator) -> None:
    """disconnect() removes the consumer from the channel group without errors."""
    await communicator.connect()
    await communicator.receive_json_from()  # discard connected event
    await communicator.disconnect()


@pytest.mark.asyncio()
@override_settings(CHANNEL_LAYERS=CHANNEL_LAYERS_OVERRIDE)
async def test_receive_stop_event_closes_connection(communicator) -> None:
    """Receiving a stop control event closes the WebSocket connection."""
    await communicator.connect()
    await communicator.receive_json_from()  # discard connected event
    await communicator.send_json_to({"event": "stop"})
    close_message = await communicator.receive_output()
    assert close_message["type"] == "websocket.close"


@pytest.mark.asyncio()
@override_settings(CHANNEL_LAYERS=CHANNEL_LAYERS_OVERRIDE)
async def test_receive_unknown_event_returns_error(communicator) -> None:
    """Receiving an unknown control event returns an error response."""
    await communicator.connect()
    await communicator.receive_json_from()  # discard connected event
    await communicator.send_json_to({"event": "unknown_event"})
    response = await communicator.receive_json_from()
    assert response["event"] == "error"
    assert "unknown_event" in response["detail"]
    await communicator.disconnect()


@pytest.mark.asyncio()
@override_settings(CHANNEL_LAYERS=CHANNEL_LAYERS_OVERRIDE)
async def test_receive_invalid_json_returns_error(communicator) -> None:
    """Receiving invalid JSON text returns an error response."""
    await communicator.connect()
    await communicator.receive_json_from()  # discard connected event
    await communicator.send_to(text_data="not valid json{{{")
    response = await communicator.receive_json_from()
    assert response["event"] == "error"
    await communicator.disconnect()


@pytest.mark.asyncio()
@override_settings(CHANNEL_LAYERS=CHANNEL_LAYERS_OVERRIDE)
async def test_receive_binary_broadcasts_to_group(communicator) -> None:
    """Receiving binary audio broadcasts a stream.media message to the channel group."""

    await communicator.connect()
    await communicator.receive_json_from()  # discard connected event

    audio_bytes = b"\x00\x01\x02\x03"
    await communicator.send_to(bytes_data=audio_bytes)

    # The group send from _handle_audio is received by stream_media on the same consumer.
    response = await communicator.receive_json_from()
    assert response["event"] == "media"
    assert response["payload"] == audio_bytes.hex()
    await communicator.disconnect()


@pytest.mark.asyncio()
@override_settings(CHANNEL_LAYERS=CHANNEL_LAYERS_OVERRIDE)
async def test_stream_media_forwards_to_client(communicator) -> None:
    """stream_media channel-layer handler forwards payload to the WebSocket client."""
    from channels.layers import get_channel_layer

    await communicator.connect()
    await communicator.receive_json_from()  # discard connected event

    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"stream_{CALL_SID}", {"type": "stream.media", "payload": "deadbeef"}
    )
    response = await communicator.receive_json_from()
    assert response["event"] == "media"
    assert response["payload"] == "deadbeef"
    await communicator.disconnect()


@pytest.mark.asyncio()
@override_settings(CHANNEL_LAYERS=CHANNEL_LAYERS_OVERRIDE)
async def test_stream_transcript_forwards_to_client(communicator) -> None:
    """stream_transcript channel-layer handler forwards text and is_final flag."""
    from channels.layers import get_channel_layer

    await communicator.connect()
    await communicator.receive_json_from()  # discard connected event

    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"stream_{CALL_SID}",
        {"type": "stream.transcript", "text": "Hello world", "is_final": True},
    )
    response = await communicator.receive_json_from()
    assert response["event"] == "transcript"
    assert response["text"] == "Hello world"
    assert response["is_final"] is True
    await communicator.disconnect()


@pytest.mark.asyncio()
@override_settings(CHANNEL_LAYERS=CHANNEL_LAYERS_OVERRIDE)
async def test_stream_transcript_defaults_is_final_to_false(communicator) -> None:
    """stream_transcript defaults is_final to False when the key is absent."""
    from channels.layers import get_channel_layer

    await communicator.connect()
    await communicator.receive_json_from()  # discard connected event

    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"stream_{CALL_SID}", {"type": "stream.transcript", "text": "Partial"}
    )
    response = await communicator.receive_json_from()
    assert response["is_final"] is False
    await communicator.disconnect()


@pytest.mark.asyncio()
@override_settings(CHANNEL_LAYERS=CHANNEL_LAYERS_OVERRIDE)
async def test_stream_response_forwards_to_client(communicator) -> None:
    """stream_response channel-layer handler forwards AI response text."""
    from channels.layers import get_channel_layer

    await communicator.connect()
    await communicator.receive_json_from()  # discard connected event

    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"stream_{CALL_SID}", {"type": "stream.response", "text": "How can I help?"}
    )
    response = await communicator.receive_json_from()
    assert response["event"] == "response"
    assert response["text"] == "How can I help?"
    await communicator.disconnect()
