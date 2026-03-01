"""Tests for phone_numbers.models."""

from phone_numbers.models import PhoneNumber


def test_phone_number_str() -> None:
    """PhoneNumber.__str__ returns the E.164 phone number."""
    number = PhoneNumber(phone_number="+4930123456789")
    assert str(number) == "+4930123456789"


def test_phone_number_default_status() -> None:
    """New phone numbers default to ACTIVE status."""
    number = PhoneNumber(phone_number="+4930123456789")
    assert number.status == PhoneNumber.Status.ACTIVE


def test_phone_number_default_number_type() -> None:
    """New phone numbers default to LOCAL type."""
    number = PhoneNumber(phone_number="+4930123456789")
    assert number.number_type == PhoneNumber.NumberType.LOCAL


def test_phone_number_default_iso_country() -> None:
    """New phone numbers default to DE country code."""
    number = PhoneNumber(phone_number="+4930123456789")
    assert number.iso_country == "DE"
