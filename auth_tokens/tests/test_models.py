"""Tests for auth_tokens.models."""

import pytest

from auth_tokens.models import APIKey, _generate_key


@pytest.mark.django_db()
def test_api_key_str(api_key: APIKey) -> None:
    """APIKey.__str__ includes the name and username."""
    assert "Test Key" in str(api_key)
    assert "testuser" in str(api_key)


@pytest.mark.django_db()
def test_api_key_default_is_active(user) -> None:
    """New API keys are active by default."""
    key = APIKey.objects.create(user=user, name="Fresh Key")
    assert key.is_active is True


@pytest.mark.django_db()
def test_api_key_last_used_at_is_null_by_default(user) -> None:
    """New API keys have no last_used_at timestamp."""
    key = APIKey.objects.create(user=user, name="Fresh Key")
    assert key.last_used_at is None


def test_generate_key_returns_64_hex_chars() -> None:
    """_generate_key returns a 64-character hexadecimal string."""
    key = _generate_key()
    assert len(key) == 64
    assert all(c in "0123456789abcdef" for c in key)


def test_generate_key_is_unique() -> None:
    """_generate_key generates unique values."""
    assert _generate_key() != _generate_key()
