import uuid

from django.db import models


class Trunk(models.Model):
    """SIP Trunk configuration for connecting to carrier networks."""

    sid = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False, db_index=True
    )
    friendly_name = models.CharField(max_length=255)
    domain_name = models.CharField(
        max_length=255,
        unique=True,
        help_text="SIP domain name for this trunk (e.g. trunk.example.pstn.twilio.com).",
    )
    disaster_recovery_url = models.URLField(
        blank=True,
        help_text="Fallback URL for call control when primary URL is unavailable.",
    )
    disaster_recovery_method = models.CharField(
        max_length=6,
        choices=[("GET", "GET"), ("POST", "POST")],
        default="POST",
    )
    recording_enabled = models.BooleanField(default=False)
    secure = models.BooleanField(
        default=True, help_text="Enforce SRTP/TLS for media and SIP."
    )
    cnam_lookup_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.friendly_name} ({self.domain_name})"
