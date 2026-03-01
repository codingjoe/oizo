"""Shared pytest fixtures for the Oizo Voice API test suite."""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from auth_tokens.models import APIKey
from billing.models import UsageRecord, Wallet
from calls.models import Call
from phone_numbers.models import PhoneNumber
from webhooks.models import WebhookEndpoint


@pytest.fixture()
def user(db) -> User:
    """Return a standard test user."""
    return User.objects.create_user(username="testuser", password="testpass123")


@pytest.fixture()
def api_key(user: User) -> APIKey:
    """Return an active API key for the test user."""
    return APIKey.objects.create(user=user, name="Test Key")


@pytest.fixture()
def api_client(api_key: APIKey) -> APIClient:
    """Return an API client authenticated via Bearer token."""
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {api_key.key}")
    return client


@pytest.fixture()
def phone_number(db) -> PhoneNumber:
    """Return a provisioned phone number."""
    return PhoneNumber.objects.create(phone_number="+4930123456789", iso_country="DE")


@pytest.fixture()
def call(db) -> Call:
    """Return a ringing outbound call."""
    return Call.objects.create(
        from_number="+4930123456789",
        to_number="+4930987654321",
        status=Call.Status.RINGING,
    )


@pytest.fixture()
def webhook_endpoint(user: User) -> WebhookEndpoint:
    """Return a webhook endpoint registered for the test user."""
    return WebhookEndpoint.objects.create(user=user, url="https://example.com/webhook")


@pytest.fixture()
def wallet(api_key: APIKey) -> Wallet:
    """Return a prepaid wallet for the test API key."""
    return Wallet.objects.create(api_key=api_key, balance="10.0000")


@pytest.fixture()
def usage_record(api_key: APIKey) -> UsageRecord:
    """Return a usage record for the test API key."""
    return UsageRecord.objects.create(
        api_key=api_key,
        resource_type=UsageRecord.ResourceType.OUTBOUND_CALL,
        call_sid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        duration_seconds=60,
        amount="0.0500",
    )
