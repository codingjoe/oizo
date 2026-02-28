import uuid

from django.db import models

from auth_tokens.models import APIKey


class UsageRecord(models.Model):
    """Tracks billable usage per call, per API key."""

    class ResourceType(models.TextChoices):
        OUTBOUND_CALL = "outbound-call", "Outbound Call"
        INBOUND_CALL = "inbound-call", "Inbound Call"
        RECORDING = "recording", "Recording"

    sid = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False, db_index=True
    )
    api_key = models.ForeignKey(
        APIKey, on_delete=models.SET_NULL, null=True, blank=True
    )
    resource_type = models.CharField(max_length=30, choices=ResourceType)
    # Reference to the related call SID (stored as string to avoid circular imports)
    call_sid = models.CharField(max_length=36, blank=True, db_index=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    amount = models.DecimalField(
        max_digits=12, decimal_places=4, help_text="Billed amount in EUR."
    )
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"{self.resource_type} {self.call_sid} — €{self.amount}"


class Wallet(models.Model):
    """Prepaid balance per API key."""

    api_key = models.OneToOneField(
        APIKey, on_delete=models.CASCADE, related_name="wallet"
    )
    balance = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.api_key.name}: €{self.balance}"
