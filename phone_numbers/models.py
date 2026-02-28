import uuid

from django.db import models


class PhoneNumber(models.Model):
    """A provisioned phone number on the platform."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        RELEASED = "released", "Released"

    class NumberType(models.TextChoices):
        LOCAL = "local", "Local"
        MOBILE = "mobile", "Mobile"
        TOLL_FREE = "toll-free", "Toll Free"

    sid = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False, db_index=True
    )
    phone_number = models.CharField(
        max_length=30,
        unique=True,
        help_text="E.164 formatted number, e.g. +4930123456789.",
    )
    friendly_name = models.CharField(max_length=255, blank=True)
    iso_country = models.CharField(
        max_length=2, default="DE", help_text="ISO 3166-1 alpha-2."
    )
    number_type = models.CharField(
        max_length=20, choices=NumberType, default=NumberType.LOCAL
    )
    status = models.CharField(max_length=20, choices=Status, default=Status.ACTIVE)

    # Inbound routing
    voice_url = models.URLField(
        blank=True,
        help_text="Webhook URL called when this number receives an inbound call.",
    )
    voice_method = models.CharField(
        max_length=4,
        choices=[("GET", "GET"), ("POST", "POST")],
        default="POST",
    )

    # Sipgate integration
    sipgate_id = models.CharField(
        max_length=100, blank=True, help_text="Internal Sipgate phoneline/routing ID."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.phone_number
