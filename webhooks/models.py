import uuid

from django.contrib.auth.models import User
from django.db import models


class WebhookEndpoint(models.Model):
    """A registered webhook endpoint that receives call-event notifications."""

    class Event(models.TextChoices):
        CALL_INITIATED = "call.initiated", "Call Initiated"
        CALL_RINGING = "call.ringing", "Call Ringing"
        CALL_ANSWERED = "call.answered", "Call Answered"
        CALL_COMPLETED = "call.completed", "Call Completed"
        CALL_FAILED = "call.failed", "Call Failed"
        RECORDING_AVAILABLE = "recording.available", "Recording Available"

    sid = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False, db_index=True
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="webhook_endpoints"
    )
    url = models.URLField(help_text="HTTPS endpoint to receive event payloads.")
    events = models.JSONField(
        default=list,
        help_text="List of event types to subscribe to. Empty list = all events.",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.url} ({self.user})"


class WebhookDelivery(models.Model):
    """Records a single webhook delivery attempt."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"

    sid = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False, db_index=True
    )
    endpoint = models.ForeignKey(
        WebhookEndpoint, on_delete=models.CASCADE, related_name="deliveries"
    )
    event_type = models.CharField(max_length=50)
    payload = models.JSONField()
    status = models.CharField(max_length=20, choices=Status, default=Status.PENDING)
    response_status_code = models.PositiveSmallIntegerField(null=True, blank=True)
    attempt_count = models.PositiveSmallIntegerField(default=0)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.event_type} → {self.endpoint.url} [{self.status}]"
