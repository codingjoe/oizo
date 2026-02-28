"""Tests for auth_tokens.authentication."""

import pytest
from django.test import RequestFactory
from rest_framework.exceptions import AuthenticationFailed

from auth_tokens.authentication import APIKeyAuthentication
from auth_tokens.models import APIKey


@pytest.fixture()
def authenticator() -> APIKeyAuthentication:
    """Return an APIKeyAuthentication instance."""
    return APIKeyAuthentication()


@pytest.fixture()
def factory() -> RequestFactory:
    """Return a Django request factory."""
    return RequestFactory()


def test_authenticate_header(authenticator: APIKeyAuthentication) -> None:
    """authenticate_header returns the Bearer keyword."""
    assert authenticator.authenticate_header(None) == "Bearer"


@pytest.mark.django_db()
def test_authenticate_returns_none_without_header(
    authenticator: APIKeyAuthentication, factory: RequestFactory
) -> None:
    """authenticate returns None when no Authorization header is present."""
    request = factory.get("/")
    assert authenticator.authenticate(request) is None


@pytest.mark.django_db()
def test_authenticate_returns_none_with_wrong_scheme(
    authenticator: APIKeyAuthentication, factory: RequestFactory
) -> None:
    """authenticate returns None when scheme is not Bearer."""
    request = factory.get("/", HTTP_AUTHORIZATION="Basic abc123")
    assert authenticator.authenticate(request) is None


@pytest.mark.django_db()
def test_authenticate_raises_for_invalid_key(
    authenticator: APIKeyAuthentication, factory: RequestFactory
) -> None:
    """authenticate raises AuthenticationFailed for an unknown key."""
    request = factory.get("/", HTTP_AUTHORIZATION="Bearer invalid-key")
    with pytest.raises(AuthenticationFailed):
        authenticator.authenticate(request)


@pytest.mark.django_db()
def test_authenticate_raises_for_inactive_key(
    authenticator: APIKeyAuthentication, factory: RequestFactory, api_key: APIKey
) -> None:
    """authenticate raises AuthenticationFailed for an inactive key."""
    api_key.is_active = False
    api_key.save()
    request = factory.get("/", HTTP_AUTHORIZATION=f"Bearer {api_key.key}")
    with pytest.raises(AuthenticationFailed):
        authenticator.authenticate(request)


@pytest.mark.django_db()
def test_authenticate_succeeds_with_valid_key(
    authenticator: APIKeyAuthentication, factory: RequestFactory, api_key: APIKey
) -> None:
    """authenticate returns (user, api_key) for a valid active key."""
    request = factory.get("/", HTTP_AUTHORIZATION=f"Bearer {api_key.key}")
    user, token = authenticator.authenticate(request)
    assert user == api_key.user
    assert token == api_key


@pytest.mark.django_db()
def test_authenticate_updates_last_used_at(
    authenticator: APIKeyAuthentication, factory: RequestFactory, api_key: APIKey
) -> None:
    """authenticate sets last_used_at on successful authentication."""
    assert api_key.last_used_at is None
    request = factory.get("/", HTTP_AUTHORIZATION=f"Bearer {api_key.key}")
    authenticator.authenticate(request)
    api_key.refresh_from_db()
    assert api_key.last_used_at is not None
