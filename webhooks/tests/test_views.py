"""Tests for webhooks.views."""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from webhooks.models import WebhookEndpoint


@pytest.mark.django_db()
def test_list_webhook_endpoints_requires_authentication() -> None:
    """Unauthenticated requests to the webhook list are rejected."""
    response = APIClient().get(reverse("webhook-list"))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db()
def test_list_webhook_endpoints_returns_own_endpoints(
    api_client: APIClient, webhook_endpoint: WebhookEndpoint
) -> None:
    """Authenticated clients see only their own webhook endpoints."""
    response = api_client.get(reverse("webhook-list"))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1


@pytest.mark.django_db()
def test_list_webhook_endpoints_excludes_other_users_endpoints(
    api_client: APIClient, webhook_endpoint: WebhookEndpoint
) -> None:
    """Webhook list does not include endpoints belonging to other users."""
    other_user = User.objects.create_user(username="other", password="pass")
    WebhookEndpoint.objects.create(user=other_user, url="https://other.example.com/wh")
    response = api_client.get(reverse("webhook-list"))
    assert response.data["count"] == 1


@pytest.mark.django_db()
def test_create_webhook_endpoint(api_client: APIClient, user: User) -> None:
    """POST /v1/webhooks/ registers a new webhook endpoint."""
    response = api_client.post(
        reverse("webhook-list"),
        {"url": "https://example.com/new-hook", "events": []},
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert WebhookEndpoint.objects.filter(user=user).exists()


@pytest.mark.django_db()
def test_create_webhook_endpoint_associates_with_current_user(
    api_client: APIClient, user: User
) -> None:
    """Newly created webhook endpoints are assigned to the authenticated user."""
    api_client.post(
        reverse("webhook-list"),
        {"url": "https://example.com/hook", "events": []},
        format="json",
    )
    endpoint = WebhookEndpoint.objects.get(url="https://example.com/hook")
    assert endpoint.user == user


@pytest.mark.django_db()
def test_retrieve_webhook_endpoint(
    api_client: APIClient, webhook_endpoint: WebhookEndpoint
) -> None:
    """GET /v1/webhooks/{sid}/ returns the webhook endpoint detail."""
    response = api_client.get(
        reverse("webhook-detail", kwargs={"sid": webhook_endpoint.sid})
    )
    assert response.status_code == status.HTTP_200_OK
    assert str(response.data["sid"]) == str(webhook_endpoint.sid)


@pytest.mark.django_db()
def test_update_webhook_endpoint(
    api_client: APIClient, webhook_endpoint: WebhookEndpoint
) -> None:
    """PATCH /v1/webhooks/{sid}/ updates the endpoint."""
    response = api_client.patch(
        reverse("webhook-detail", kwargs={"sid": webhook_endpoint.sid}),
        {"is_active": False},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    webhook_endpoint.refresh_from_db()
    assert webhook_endpoint.is_active is False


@pytest.mark.django_db()
def test_schema_generation_returns_empty_queryset(user: User) -> None:
    """get_queryset returns an empty queryset during schema generation."""
    from webhooks.views import WebhookEndpointViewSet

    viewset = WebhookEndpointViewSet()
    viewset.swagger_fake_view = True
    assert list(viewset.get_queryset()) == []


@pytest.mark.django_db()
def test_delete_webhook_endpoint(
    api_client: APIClient, webhook_endpoint: WebhookEndpoint
) -> None:
    """DELETE /v1/webhooks/{sid}/ removes the webhook endpoint."""
    response = api_client.delete(
        reverse("webhook-detail", kwargs={"sid": webhook_endpoint.sid})
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not WebhookEndpoint.objects.filter(sid=webhook_endpoint.sid).exists()
