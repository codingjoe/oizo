"""Tests for calls.serializers."""

import pytest

from calls.models import Call
from calls.serializers import CallCreateSerializer, CallSerializer


@pytest.mark.django_db()
def test_call_serializer_read_only_fields(call: Call) -> None:
    """CallSerializer marks status, timing fields, and sid as read-only."""
    serializer = CallSerializer(call)
    data = serializer.data
    assert "sid" in data
    assert "status" in data
    assert "from_number" in data


@pytest.mark.django_db()
def test_call_create_serializer_valid() -> None:
    """CallCreateSerializer accepts from_number and to_number."""
    serializer = CallCreateSerializer(
        data={"from_number": "+4930123456789", "to_number": "+4930987654321"}
    )
    assert serializer.is_valid()


@pytest.mark.django_db()
def test_call_create_serializer_requires_from_number() -> None:
    """CallCreateSerializer rejects data missing from_number."""
    serializer = CallCreateSerializer(data={"to_number": "+4930987654321"})
    assert not serializer.is_valid()
    assert "from_number" in serializer.errors


@pytest.mark.django_db()
def test_call_create_serializer_requires_to_number() -> None:
    """CallCreateSerializer rejects data missing to_number."""
    serializer = CallCreateSerializer(data={"from_number": "+4930123456789"})
    assert not serializer.is_valid()
    assert "to_number" in serializer.errors
