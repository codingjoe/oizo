"""Tests for billing.views."""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from auth_tokens.models import APIKey
from billing.models import UsageRecord, Wallet


@pytest.mark.django_db()
def test_list_usage_records_requires_authentication() -> None:
    """Unauthenticated requests to the usage list are rejected."""
    response = APIClient().get(reverse("usage-list"))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db()
def test_list_usage_records_returns_own_records(
    api_client: APIClient, usage_record: UsageRecord
) -> None:
    """Authenticated clients see only their own usage records."""
    response = api_client.get(reverse("usage-list"))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1


@pytest.mark.django_db()
def test_list_usage_records_filters_by_resource_type(
    api_client: APIClient, usage_record: UsageRecord
) -> None:
    """Usage records can be filtered by resource_type."""
    url = reverse("usage-list")
    response = api_client.get(url, {"resource_type": "inbound-call"})
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0


@pytest.mark.django_db()
def test_list_usage_records_filters_by_call_sid(
    api_client: APIClient, usage_record: UsageRecord
) -> None:
    """Usage records can be filtered by call_sid."""
    url = reverse("usage-list")
    response = api_client.get(url, {"call_sid": usage_record.call_sid})
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1


@pytest.mark.django_db()
def test_wallet_view_requires_authentication() -> None:
    """Unauthenticated requests to the wallet endpoint are rejected."""
    response = APIClient().get(reverse("wallet"))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db()
def test_wallet_view_returns_balance_for_api_key_auth(
    api_client: APIClient, wallet: Wallet
) -> None:
    """Wallet endpoint returns the balance for Bearer-authenticated clients."""
    response = api_client.get(reverse("wallet"))
    assert response.status_code == status.HTTP_200_OK
    assert "balance" in response.data


@pytest.mark.django_db()
def test_wallet_view_creates_wallet_if_missing(
    api_client: APIClient, api_key: APIKey
) -> None:
    """Wallet endpoint creates a wallet on first access when none exists."""
    assert not Wallet.objects.filter(api_key=api_key).exists()
    response = api_client.get(reverse("wallet"))
    assert response.status_code == status.HTTP_200_OK
    assert Wallet.objects.filter(api_key=api_key).exists()


@pytest.mark.django_db()
def test_wallet_view_returns_zero_balance_for_session_auth_without_key(
    client, user
) -> None:
    """Session-authenticated users without an API key receive a zero balance."""
    client.force_login(user)
    response = client.get(reverse("wallet"))
    assert response.status_code == status.HTTP_200_OK
    assert float(response.data["balance"]) == 0


@pytest.mark.django_db()
def test_wallet_view_falls_back_to_first_key_for_session_auth(
    client, user, api_key: APIKey, wallet: Wallet
) -> None:
    """Session-authenticated users with an API key receive their wallet."""
    client.force_login(user)
    response = client.get(reverse("wallet"))
    assert response.status_code == status.HTTP_200_OK
    assert str(response.data["balance"]) == str(wallet.balance)
