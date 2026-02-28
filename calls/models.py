import uuid

from django.db import models


class Call(models.Model):
    """Represents a phone call, similar to a Twilio Call resource."""

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RINGING = "ringing", "Ringing"
        IN_PROGRESS = "in-progress", "In Progress"
        COMPLETED = "completed", "Completed"
        BUSY = "busy", "Busy"
        FAILED = "failed", "Failed"
        NO_ANSWER = "no-answer", "No Answer"
        CANCELED = "canceled", "Canceled"

    class Direction(models.TextChoices):
        INBOUND = "inbound", "Inbound"
        OUTBOUND_API = "outbound-api", "Outbound API"
        OUTBOUND_DIAL = "outbound-dial", "Outbound Dial"

    sid = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False, db_index=True
    )
    status = models.CharField(max_length=20, choices=Status, default=Status.QUEUED)
    direction = models.CharField(
        max_length=20, choices=Direction, default=Direction.OUTBOUND_API
    )
    from_number = models.CharField(max_length=100)
    to_number = models.CharField(max_length=100)
    url = models.URLField(
        blank=True,
        help_text="Webhook URL for call control instructions (TwiML-compatible).",
    )
    status_callback = models.URLField(
        blank=True, help_text="URL to receive call status change notifications."
    )
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.PositiveIntegerField(
        null=True, blank=True, help_text="Duration in seconds."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Call {self.sid} ({self.status})"
