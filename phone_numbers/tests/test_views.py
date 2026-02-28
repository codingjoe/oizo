"""Tests for phone_numbers.views."""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from phone_numbers.models import PhoneNumber


@pytest.mark.django_db()
def test_list_phone_numbers(api_client: APIClient, phone_number: PhoneNumber) -> None:
    """GET /v1/numbers/ returns a paginated list of phone numbers."""
    response = api_client.get(reverse("phonenumber-list"))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1


@pytest.mark.django_db()
def test_create_phone_number(api_client: APIClient) -> None:
    """POST /v1/numbers/ provisions a new phone number."""
    response = api_client.post(
        reverse("phonenumber-list"),
        {"phone_number": "+4930000000001", "iso_country": "DE"},
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert "sid" in response.data


@pytest.mark.django_db()
def test_retrieve_phone_number(
    api_client: APIClient, phone_number: PhoneNumber
) -> None:
    """GET /v1/numbers/{sid}/ returns the phone number detail."""
    response = api_client.get(
        reverse("phonenumber-detail", kwargs={"sid": phone_number.sid})
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["phone_number"] == phone_number.phone_number


@pytest.mark.django_db()
def test_update_voice_url(api_client: APIClient, phone_number: PhoneNumber) -> None:
    """PATCH /v1/numbers/{sid}/ updates the inbound voice webhook URL."""
    response = api_client.patch(
        reverse("phonenumber-detail", kwargs={"sid": phone_number.sid}),
        {"voice_url": "https://example.com/inbound"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    phone_number.refresh_from_db()
    assert phone_number.voice_url == "https://example.com/inbound"


@pytest.mark.django_db()
def test_delete_phone_number(api_client: APIClient, phone_number: PhoneNumber) -> None:
    """DELETE /v1/numbers/{sid}/ removes the phone number."""
    response = api_client.delete(
        reverse("phonenumber-detail", kwargs={"sid": phone_number.sid})
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not PhoneNumber.objects.filter(sid=phone_number.sid).exists()
