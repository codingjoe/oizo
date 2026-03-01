"""Tests for calls.models."""

import pytest

from calls.models import Call


def test_call_str() -> None:
    """Call.__str__ includes the SID and status."""
    call = Call(sid="00000000-0000-0000-0000-000000000001", status=Call.Status.INIT)
    assert "init" in str(call)


def test_call_default_status() -> None:
    """New calls default to INIT status."""
    call = Call(from_number="+4930123456789", to_number="+4930987654321")
    assert call.status == Call.Status.INIT


def test_call_default_direction() -> None:
    """New calls default to outbound-api direction."""
    call = Call(from_number="+4930123456789", to_number="+4930987654321")
    assert call.direction == Call.Direction.OUTBOUND_API


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (Call.Status.COMPLETED, True),
        (Call.Status.FAILED, True),
        (Call.Status.DENIED, True),
        (Call.Status.CANCELED, True),
        (Call.Status.INIT, False),
        (Call.Status.VALIDATE, False),
        (Call.Status.ROUTE, False),
        (Call.Status.RINGING, False),
        (Call.Status.ANSWERED, False),
    ],
)
def test_is_terminal(status: str, expected: bool) -> None:
    """is_terminal reflects whether the call has reached a terminal state."""
    call = Call(status=status)
    assert call.is_terminal is expected
