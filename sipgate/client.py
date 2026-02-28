"""
Sipgate REST API client.

Used for number provisioning and account information.
All configuration is read from Django settings / environment variables.
"""

import logging

from django.conf import settings

logger = logging.getLogger(__name__)

_DEFAULT_BASE_URL = "https://api.sipgate.com/v2"


def _get_session():
    """Return an HTTP session pre-configured with Sipgate credentials."""
    import requests

    session = requests.Session()
    token_id = getattr(settings, "SIPGATE_TOKEN_ID", "")
    token = getattr(settings, "SIPGATE_TOKEN", "")
    if token_id and token:
        session.auth = (token_id, token)
    session.headers.update(
        {"Accept": "application/json", "Content-Type": "application/json"}
    )
    return session


def _base_url() -> str:
    return getattr(settings, "SIPGATE_BASE_URL", _DEFAULT_BASE_URL).rstrip("/")


def get_account_info() -> dict:
    """Fetch authenticated account information from Sipgate."""
    session = _get_session()
    resp = session.get(f"{_base_url()}/account")
    resp.raise_for_status()
    return resp.json()


def list_phone_lines() -> list[dict]:
    """List all phone lines (SIPID/extension) on the account."""
    session = _get_session()
    resp = session.get(f"{_base_url()}/phonelines")
    resp.raise_for_status()
    return resp.json().get("items", [])


def initiate_call(caller: str, callee: str, call_id: str | None = None) -> dict:
    """
    Initiate an outbound call via the Sipgate REST 'sessions/calls' endpoint.

    Returns the Sipgate session ID.
    """
    session = _get_session()
    payload: dict = {"caller": caller, "callee": callee}
    if call_id:
        payload["callerId"] = call_id
    resp = session.post(f"{_base_url()}/sessions/calls", json=payload)
    resp.raise_for_status()
    return resp.json()


def hangup_call(sipgate_session_id: str) -> None:
    """Hang up an active call identified by its Sipgate session ID."""
    session = _get_session()
    resp = session.delete(f"{_base_url()}/calls/{sipgate_session_id}")
    # 204 No Content is the expected success response
    if resp.status_code not in (200, 204):
        resp.raise_for_status()
