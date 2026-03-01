"""Tests for webhooks.dispatch."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from webhooks.dispatch import dispatch_event
from webhooks.models import WebhookDelivery, WebhookEndpoint


@pytest.mark.django_db()
def test_dispatch_event_delivers_to_active_endpoint(
    webhook_endpoint: WebhookEndpoint,
) -> None:
    """dispatch_event sends a delivery to all active endpoints."""
    with patch("webhooks.dispatch.requests.post") as mock_post:
        mock_post.return_value = MagicMock(ok=True, status_code=200)
        dispatch_event("call.initiated", {"call_sid": "abc"})
    assert WebhookDelivery.objects.filter(
        endpoint=webhook_endpoint, status=WebhookDelivery.Status.DELIVERED
    ).exists()


@pytest.mark.django_db()
def test_dispatch_event_skips_inactive_endpoint(
    webhook_endpoint: WebhookEndpoint,
) -> None:
    """dispatch_event ignores inactive endpoints."""
    webhook_endpoint.is_active = False
    webhook_endpoint.save()
    with patch("webhooks.dispatch.requests.post") as mock_post:
        dispatch_event("call.initiated", {"call_sid": "abc"})
    mock_post.assert_not_called()


@pytest.mark.django_db()
def test_dispatch_event_filters_by_subscribed_events(
    user, webhook_endpoint: WebhookEndpoint
) -> None:
    """dispatch_event skips endpoints not subscribed to the given event type."""
    webhook_endpoint.events = ["call.completed"]
    webhook_endpoint.save()
    with patch("webhooks.dispatch.requests.post") as mock_post:
        dispatch_event("call.initiated", {"call_sid": "abc"})
    mock_post.assert_not_called()


@pytest.mark.django_db()
def test_dispatch_event_delivers_when_event_matches_subscription(
    webhook_endpoint: WebhookEndpoint,
) -> None:
    """dispatch_event delivers when endpoint subscribes to the given event."""
    webhook_endpoint.events = ["call.initiated"]
    webhook_endpoint.save()
    with patch("webhooks.dispatch.requests.post") as mock_post:
        mock_post.return_value = MagicMock(ok=True, status_code=200)
        dispatch_event("call.initiated", {"call_sid": "abc"})
    assert WebhookDelivery.objects.filter(
        status=WebhookDelivery.Status.DELIVERED
    ).exists()


@pytest.mark.django_db()
def test_dispatch_event_filters_by_user(
    user, webhook_endpoint: WebhookEndpoint
) -> None:
    """dispatch_event scopes delivery to the given user's endpoints."""
    from django.contrib.auth.models import User

    other_user = User.objects.create_user(username="other", password="pass")
    WebhookEndpoint.objects.create(user=other_user, url="https://other.example.com/wh")

    with patch("webhooks.dispatch.requests.post") as mock_post:
        mock_post.return_value = MagicMock(ok=True, status_code=200)
        dispatch_event("call.initiated", {"call_sid": "abc"}, user=user)

    assert WebhookDelivery.objects.count() == 1
    assert WebhookDelivery.objects.first().endpoint == webhook_endpoint


@pytest.mark.django_db()
def test_dispatch_event_marks_failed_on_non_ok_response(
    webhook_endpoint: WebhookEndpoint,
) -> None:
    """dispatch_event marks the delivery as failed on a non-2xx response."""
    with patch("webhooks.dispatch.requests.post") as mock_post:
        mock_post.return_value = MagicMock(ok=False, status_code=500)
        dispatch_event("call.initiated", {"call_sid": "abc"})
    assert WebhookDelivery.objects.filter(status=WebhookDelivery.Status.FAILED).exists()


@pytest.mark.django_db()
def test_dispatch_event_marks_failed_on_request_exception(
    webhook_endpoint: WebhookEndpoint,
) -> None:
    """dispatch_event marks the delivery as failed when a network error occurs."""
    with patch("webhooks.dispatch.requests.post") as mock_post:
        mock_post.side_effect = requests.RequestException("connection refused")
        dispatch_event("call.initiated", {"call_sid": "abc"})
    assert WebhookDelivery.objects.filter(status=WebhookDelivery.Status.FAILED).exists()


@pytest.mark.django_db()
def test_dispatch_event_increments_attempt_count(
    webhook_endpoint: WebhookEndpoint,
) -> None:
    """dispatch_event increments the attempt counter on each delivery."""
    with patch("webhooks.dispatch.requests.post") as mock_post:
        mock_post.return_value = MagicMock(ok=True, status_code=200)
        dispatch_event("call.initiated", {"call_sid": "abc"})
    delivery = WebhookDelivery.objects.first()
    assert delivery.attempt_count == 1
