import secrets

from django.contrib.auth.models import User
from django.db import models


def _generate_key():
    return secrets.token_hex(32)


class APIKey(models.Model):
    """Per-client API key for authenticating platform requests."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="api_keys")
    key = models.CharField(
        max_length=64, unique=True, default=_generate_key, editable=False
    )
    name = models.CharField(
        max_length=255, help_text="Human-readable label for this API key."
    )
    is_active = models.BooleanField(default=True)
    # Spending / rate limits
    spending_limit = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Hard spending cap in EUR. NULL means no cap.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.user})"
