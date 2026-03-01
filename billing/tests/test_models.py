"""Tests for billing.models."""

import pytest

from billing.models import UsageRecord, Wallet


@pytest.mark.django_db()
def test_usage_record_str(usage_record: UsageRecord) -> None:
    """UsageRecord.__str__ includes resource type, call SID, and amount."""
    text = str(usage_record)
    assert "outbound-call" in text
    assert "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee" in text
    assert "€" in text


@pytest.mark.django_db()
def test_wallet_str(wallet: Wallet) -> None:
    """Wallet.__str__ includes the API key name and balance."""
    text = str(wallet)
    assert "Test Key" in text
    assert "€" in text
