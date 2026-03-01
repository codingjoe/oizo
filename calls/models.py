import uuid

from django.db import models


class Call(models.Model):
    """
    Represents a phone call managed by the Oizo platform.

    The call lifecycle follows this state machine:

        INIT → VALIDATE → ROUTE → RINGING → ANSWERED → COMPLETED
                       ↘ DENIED (fraud)
                                        ↘ FAILED
    """

    class Status(models.TextChoices):
        INIT = "init", "Init"
        VALIDATE = "validate", "Validate"
        ROUTE = "route", "Route"
        RINGING = "ringing", "Ringing"
        ANSWERED = "answered", "Answered"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        DENIED = "denied", "Denied (Fraud / Policy)"
        CANCELED = "canceled", "Canceled"

    class Direction(models.TextChoices):
        INBOUND = "inbound", "Inbound"
        OUTBOUND_API = "outbound-api", "Outbound API"

    sid = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False, db_index=True
    )
    status = models.CharField(max_length=20, choices=Status, default=Status.INIT)
    direction = models.CharField(
        max_length=20, choices=Direction, default=Direction.OUTBOUND_API
    )
    from_number = models.CharField(
        max_length=30, help_text="Caller ID in E.164 format, e.g. +4930123456789."
    )
    to_number = models.CharField(
        max_length=30, help_text="Destination number in E.164 format."
    )
    status_callback = models.URLField(
        blank=True, help_text="URL to receive call status change notifications."
    )
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.PositiveIntegerField(
        null=True, blank=True, help_text="Duration in seconds."
    )

    # Sipgate integration
    sipgate_session_id = models.CharField(
        max_length=100, blank=True, help_text="Sipgate session ID for active calls."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Call {self.sid} ({self.status})"

    # ------------------------------------------------------------------ #
    # Terminal states                                                       #
    # ------------------------------------------------------------------ #

    TERMINAL_STATUSES = {
        Status.COMPLETED,
        Status.FAILED,
        Status.DENIED,
        Status.CANCELED,
    }

    @property
    def is_terminal(self) -> bool:
        return self.status in self.TERMINAL_STATUSES
