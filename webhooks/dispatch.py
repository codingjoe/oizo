import logging

import requests

from .models import WebhookDelivery, WebhookEndpoint

logger = logging.getLogger(__name__)


def dispatch_event(event_type: str, payload: dict, user=None) -> None:
    """
    Create WebhookDelivery records for all active matching endpoints and
    attempt delivery synchronously (best-effort for the MVP).

    In production this should be offloaded to a Celery/background task queue.
    """
    endpoints_qs = WebhookEndpoint.objects.filter(is_active=True)
    if user is not None:
        endpoints_qs = endpoints_qs.filter(user=user)

    for endpoint in endpoints_qs:
        # Filter by subscribed events (empty list = all events)
        if endpoint.events and event_type not in endpoint.events:
            continue

        delivery = WebhookDelivery.objects.create(
            endpoint=endpoint,
            event_type=event_type,
            payload={"event": event_type, **payload},
        )
        _attempt_delivery(delivery)


def _attempt_delivery(delivery: WebhookDelivery) -> None:
    delivery.attempt_count += 1
    try:
        resp = requests.post(
            delivery.endpoint.url,
            json=delivery.payload,
            timeout=10,
            headers={
                "Content-Type": "application/json",
                "X-Oizo-Event": delivery.event_type,
            },
        )
        delivery.response_status_code = resp.status_code
        if resp.ok:
            delivery.status = WebhookDelivery.Status.DELIVERED
        else:
            delivery.status = WebhookDelivery.Status.FAILED
            logger.warning(
                "Webhook delivery %s failed: HTTP %s", delivery.sid, resp.status_code
            )
    except requests.RequestException as exc:
        delivery.status = WebhookDelivery.Status.FAILED
        logger.warning("Webhook delivery %s error: %s", delivery.sid, exc)
    delivery.save(update_fields=["status", "response_status_code", "attempt_count"])
