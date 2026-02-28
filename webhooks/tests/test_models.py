"""Tests for webhooks.models."""

import pytest

from webhooks.models import WebhookDelivery, WebhookEndpoint


@pytest.mark.django_db()
def test_webhook_endpoint_str(webhook_endpoint: WebhookEndpoint) -> None:
    """WebhookEndpoint.__str__ includes URL and username."""
    text = str(webhook_endpoint)
    assert "https://example.com/webhook" in text
    assert "testuser" in text


@pytest.mark.django_db()
def test_webhook_delivery_str(webhook_endpoint: WebhookEndpoint) -> None:
    """WebhookDelivery.__str__ includes event type, URL, and status."""
    delivery = WebhookDelivery.objects.create(
        endpoint=webhook_endpoint,
        event_type="call.initiated",
        payload={"event": "call.initiated"},
    )
    text = str(delivery)
    assert "call.initiated" in text
    assert "https://example.com/webhook" in text
    assert "pending" in text
