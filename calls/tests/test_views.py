"""Tests for calls.views."""

from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from calls.models import Call


@pytest.mark.django_db()
def test_list_calls(api_client: APIClient, call: Call) -> None:
    """GET /v1/calls/ returns a paginated list of calls."""
    response = api_client.get(reverse("call-list"))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1


@pytest.mark.django_db()
@patch("calls.views.sipgate.initiate_call")
def test_create_call_transitions_to_ringing(
    mock_initiate, api_client: APIClient
) -> None:
    """POST /v1/calls/ initiates a Sipgate call and returns RINGING status."""
    mock_initiate.return_value = {"sessionId": "sg-session-abc"}
    response = api_client.post(
        reverse("call-list"),
        {"from_number": "+4930123456789", "to_number": "+4930987654321"},
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["status"] == Call.Status.RINGING
    assert "sid" in response.data


@pytest.mark.django_db()
@patch("calls.views.sipgate.initiate_call")
def test_create_call_stores_sipgate_session_id(
    mock_initiate, api_client: APIClient
) -> None:
    """Successful Sipgate call stores the returned session ID."""
    mock_initiate.return_value = {"sessionId": "sg-session-abc"}
    api_client.post(
        reverse("call-list"),
        {"from_number": "+4930123456789", "to_number": "+4930987654321"},
        format="json",
    )
    call = Call.objects.first()
    assert call.sipgate_session_id == "sg-session-abc"


@pytest.mark.django_db()
@patch("calls.views.sipgate.initiate_call")
def test_create_call_transitions_to_failed_on_sipgate_error(
    mock_initiate, api_client: APIClient
) -> None:
    """POST /v1/calls/ transitions to FAILED when Sipgate raises an error."""
    mock_initiate.side_effect = Exception("carrier unavailable")
    response = api_client.post(
        reverse("call-list"),
        {"from_number": "+4930123456789", "to_number": "+4930987654321"},
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["status"] == Call.Status.FAILED


@pytest.mark.django_db()
def test_retrieve_call(api_client: APIClient, call: Call) -> None:
    """GET /v1/calls/{sid}/ returns the call detail."""
    response = api_client.get(reverse("call-detail", kwargs={"sid": call.sid}))
    assert response.status_code == status.HTTP_200_OK
    assert str(response.data["sid"]) == str(call.sid)


@pytest.mark.django_db()
@patch("calls.views.sipgate.hangup_call")
def test_delete_call_cancels_and_hangs_up(
    mock_hangup, api_client: APIClient, call: Call
) -> None:
    """DELETE /v1/calls/{sid}/ cancels the call and calls Sipgate hangup."""
    call.sipgate_session_id = "sg-123"
    call.save()
    response = api_client.delete(reverse("call-detail", kwargs={"sid": call.sid}))
    assert response.status_code == status.HTTP_200_OK
    call.refresh_from_db()
    assert call.status == Call.Status.CANCELED
    mock_hangup.assert_called_once_with("sg-123")


@pytest.mark.django_db()
@patch("calls.views.sipgate.hangup_call")
def test_delete_call_without_session_id_skips_hangup(
    mock_hangup, api_client: APIClient, call: Call
) -> None:
    """DELETE /v1/calls/{sid}/ skips Sipgate hangup when no session ID is set."""
    assert not call.sipgate_session_id
    response = api_client.delete(reverse("call-detail", kwargs={"sid": call.sid}))
    assert response.status_code == status.HTTP_200_OK
    mock_hangup.assert_not_called()


@pytest.mark.django_db()
@patch("calls.views.sipgate.hangup_call")
def test_delete_call_continues_on_hangup_error(
    mock_hangup, api_client: APIClient, call: Call
) -> None:
    """DELETE /v1/calls/{sid}/ still cancels the call even when Sipgate hangup fails."""
    call.sipgate_session_id = "sg-123"
    call.save()
    mock_hangup.side_effect = Exception("carrier error")
    response = api_client.delete(reverse("call-detail", kwargs={"sid": call.sid}))
    assert response.status_code == status.HTTP_200_OK
    call.refresh_from_db()
    assert call.status == Call.Status.CANCELED


@pytest.mark.django_db()
def test_delete_terminal_call_returns_conflict(
    api_client: APIClient, call: Call
) -> None:
    """DELETE /v1/calls/{sid}/ returns 409 when the call is already terminal."""
    call.status = Call.Status.COMPLETED
    call.save()
    response = api_client.delete(reverse("call-detail", kwargs={"sid": call.sid}))
    assert response.status_code == status.HTTP_409_CONFLICT
