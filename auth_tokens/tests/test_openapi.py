"""Tests for auth_tokens.openapi."""

from auth_tokens.openapi import APIKeyAuthenticationExtension


def test_get_security_definition_returns_bearer_scheme() -> None:
    """get_security_definition returns an HTTP Bearer security definition."""
    extension = APIKeyAuthenticationExtension(target=None)
    definition = extension.get_security_definition(auto_schema=None)
    assert definition["type"] == "http"
    assert definition["scheme"] == "bearer"
    assert "bearerFormat" in definition
    assert "description" in definition
