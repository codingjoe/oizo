"""
WebSocket consumers for real-time audio streaming.

Clients can connect to a stream to:
- Send raw audio chunks (binary frames) for speech-to-text processing.
- Receive text transcription events and AI response audio.

The consumer emits structured JSON events that clients can act upon
to integrate their own AI inference and TTS pipelines.

Event types sent to the client:
- ``transcript``: A partial or final speech-to-text transcription chunk.
- ``response``: A text response produced by the connected AI model.
- ``media``: A binary audio payload for playback (TTS output).
- ``error``: An error description.

Events received from the client:
- ``media``: Raw audio bytes (binary WebSocket frame) to transcribe.
- ``stop``: Signal to close the stream gracefully.
"""

import json

from channels.generic.websocket import AsyncWebsocketConsumer


class AudioStreamConsumer(AsyncWebsocketConsumer):
    """
    Real-time audio streaming consumer for AI voice conversations.

    Connect via WebSocket at ``/v1/streams/<call_sid>/``.
    Audio is sent as binary frames; control messages use JSON text frames.
    """

    async def connect(self):
        self.call_sid = self.scope["url_route"]["kwargs"]["call_sid"]
        self.group_name = f"stream_{self.call_sid}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send(
            text_data=json.dumps(
                {
                    "event": "connected",
                    "call_sid": str(self.call_sid),
                }
            )
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data is not None:
            await self._handle_audio(bytes_data)
        elif text_data is not None:
            await self._handle_control(text_data)

    async def _handle_audio(self, audio_bytes: bytes) -> None:
        """Process an incoming audio chunk from the client."""
        # Emit the raw audio to all group members so other consumers
        # (e.g. a recording or transcription worker) can process it.
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "stream.media",
                "payload": audio_bytes.hex(),
            },
        )

    async def _handle_control(self, text_data: str) -> None:
        """Handle a JSON control message from the client."""
        try:
            message = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(
                text_data=json.dumps({"event": "error", "detail": "Invalid JSON."})
            )
            return

        event = message.get("event")

        if event == "stop":
            await self.close()
        else:
            await self.send(
                text_data=json.dumps(
                    {"event": "error", "detail": f"Unknown event: {event!r}."}
                )
            )

    # ------------------------------------------------------------------ #
    # Channel-layer message handlers (called by group_send)               #
    # ------------------------------------------------------------------ #

    async def stream_media(self, event):
        """Forward a media chunk received from the channel layer to the client."""
        await self.send(
            text_data=json.dumps({"event": "media", "payload": event["payload"]})
        )

    async def stream_transcript(self, event):
        """Forward a transcription result to the client."""
        await self.send(
            text_data=json.dumps(
                {
                    "event": "transcript",
                    "text": event["text"],
                    "is_final": event.get("is_final", False),
                }
            )
        )

    async def stream_response(self, event):
        """Forward an AI-generated text response to the client."""
        await self.send(
            text_data=json.dumps(
                {
                    "event": "response",
                    "text": event["text"],
                }
            )
        )
