"""Tests for sipgate.client."""

from unittest.mock import MagicMock, patch

import pytest

from sipgate import client


def test_base_url_returns_default(settings) -> None:
    """_base_url returns the default Sipgate API URL when not configured."""
    assert client._base_url() == "https://api.sipgate.com/v2"


def test_base_url_uses_setting(settings) -> None:
    """_base_url returns the configured SIPGATE_BASE_URL without trailing slash."""
    settings.SIPGATE_BASE_URL = "https://custom.sipgate.example.com/v2/"
    assert client._base_url() == "https://custom.sipgate.example.com/v2"


@patch("requests.Session")
def test_get_session_without_credentials(mock_session_class, settings) -> None:
    """_get_session returns a session without auth when credentials are absent."""
    settings.SIPGATE_TOKEN_ID = ""
    settings.SIPGATE_TOKEN = ""
    session = mock_session_class.return_value
    result = client._get_session()
    assert result is session
    assert (
        session.auth is None or not hasattr(session, "auth") or session.auth != ("", "")
    )


@patch("requests.Session")
def test_get_session_with_credentials(mock_session_class, settings) -> None:
    """_get_session configures HTTP Basic auth when credentials are present."""
    settings.SIPGATE_TOKEN_ID = "token-id-123"
    settings.SIPGATE_TOKEN = "token-secret"
    session = mock_session_class.return_value
    client._get_session()
    assert session.auth == ("token-id-123", "token-secret")


@patch("sipgate.client._get_session")
def test_get_account_info(mock_get_session) -> None:
    """get_account_info fetches /account and returns parsed JSON."""
    session = MagicMock()
    mock_get_session.return_value = session
    session.get.return_value.json.return_value = {"company": "Acme"}
    result = client.get_account_info()
    assert result == {"company": "Acme"}
    session.get.return_value.raise_for_status.assert_called_once()


@patch("sipgate.client._get_session")
def test_list_phone_lines(mock_get_session) -> None:
    """list_phone_lines fetches /phonelines and returns items list."""
    session = MagicMock()
    mock_get_session.return_value = session
    session.get.return_value.json.return_value = {
        "items": [{"id": "w0", "alias": "Main"}]
    }
    result = client.list_phone_lines()
    assert result == [{"id": "w0", "alias": "Main"}]


@patch("sipgate.client._get_session")
def test_list_phone_lines_returns_empty_list_when_missing(mock_get_session) -> None:
    """list_phone_lines returns an empty list when items key is absent."""
    session = MagicMock()
    mock_get_session.return_value = session
    session.get.return_value.json.return_value = {}
    result = client.list_phone_lines()
    assert result == []


@patch("sipgate.client._get_session")
def test_initiate_call_without_caller_id(mock_get_session) -> None:
    """initiate_call posts caller and callee without callerId when omitted."""
    session = MagicMock()
    mock_get_session.return_value = session
    session.post.return_value.json.return_value = {"sessionId": "sess-1"}
    result = client.initiate_call(caller="+4930111", callee="+4930222")
    assert result == {"sessionId": "sess-1"}
    _args, kwargs = session.post.call_args
    assert kwargs["json"] == {"caller": "+4930111", "callee": "+4930222"}


@patch("sipgate.client._get_session")
def test_initiate_call_with_caller_id(mock_get_session) -> None:
    """initiate_call includes callerId in the payload when provided."""
    session = MagicMock()
    mock_get_session.return_value = session
    session.post.return_value.json.return_value = {"sessionId": "sess-2"}
    client.initiate_call(caller="+4930111", callee="+4930222", call_id="cid-99")
    _args, kwargs = session.post.call_args
    assert kwargs["json"]["callerId"] == "cid-99"


@patch("sipgate.client._get_session")
def test_hangup_call_accepts_200(mock_get_session) -> None:
    """hangup_call succeeds silently on HTTP 200."""
    session = MagicMock()
    mock_get_session.return_value = session
    session.delete.return_value.status_code = 200
    client.hangup_call("sess-abc")


@patch("sipgate.client._get_session")
def test_hangup_call_accepts_204(mock_get_session) -> None:
    """hangup_call succeeds silently on HTTP 204 No Content."""
    session = MagicMock()
    mock_get_session.return_value = session
    session.delete.return_value.status_code = 204
    client.hangup_call("sess-abc")


@patch("sipgate.client._get_session")
def test_hangup_call_raises_on_error_status(mock_get_session) -> None:
    """hangup_call raises an exception for non-success HTTP status codes."""
    session = MagicMock()
    mock_get_session.return_value = session
    session.delete.return_value.status_code = 500
    session.delete.return_value.raise_for_status.side_effect = Exception("server error")
    with pytest.raises(Exception, match="server error"):
        client.hangup_call("sess-abc")
