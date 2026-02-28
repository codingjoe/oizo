from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Call


class CallModelTest(TestCase):
    def test_str(self):
        call = Call(sid="00000000-0000-0000-0000-000000000001", status=Call.Status.INIT)
        self.assertIn("init", str(call))

    def test_default_status(self):
        call = Call(from_number="+4930123456789", to_number="+4930987654321")
        self.assertEqual(call.status, Call.Status.INIT)

    def test_default_direction(self):
        call = Call(from_number="+4930123456789", to_number="+4930987654321")
        self.assertEqual(call.direction, Call.Direction.OUTBOUND_API)

    def test_is_terminal(self):
        call = Call(status=Call.Status.COMPLETED)
        self.assertTrue(call.is_terminal)
        call.status = Call.Status.RINGING
        self.assertFalse(call.is_terminal)


class CallAPITest(APITestCase):
    def _create_call(self, **kwargs):
        defaults = {
            "from_number": "+4930123456789",
            "to_number": "+4930987654321",
            "status": Call.Status.RINGING,
        }
        defaults.update(kwargs)
        return Call.objects.create(**defaults)

    def test_list_calls(self):
        self._create_call()
        url = reverse("call-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    @patch("calls.views.sipgate.initiate_call")
    def test_create_call_success(self, mock_initiate):
        mock_initiate.return_value = {"sessionId": "sipgate-session-123"}
        url = reverse("call-list")
        data = {
            "from_number": "+4930123456789",
            "to_number": "+4930987654321",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("sid", response.data)
        self.assertEqual(response.data["status"], Call.Status.RINGING)

    @patch("calls.views.sipgate.initiate_call")
    def test_create_call_sipgate_failure(self, mock_initiate):
        mock_initiate.side_effect = Exception("Sipgate unavailable")
        url = reverse("call-list")
        data = {"from_number": "+4930123456789", "to_number": "+4930987654321"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], Call.Status.FAILED)

    def test_retrieve_call(self):
        call = self._create_call()
        url = reverse("call-detail", kwargs={"sid": call.sid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data["sid"]), str(call.sid))

    @patch("calls.views.sipgate.hangup_call")
    def test_cancel_active_call(self, mock_hangup):
        call = self._create_call(sipgate_session_id="sg-123")
        url = reverse("call-detail", kwargs={"sid": call.sid})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        call.refresh_from_db()
        self.assertEqual(call.status, Call.Status.CANCELED)
        mock_hangup.assert_called_once_with("sg-123")

    def test_cancel_terminal_call_returns_conflict(self):
        call = self._create_call(status=Call.Status.COMPLETED)
        url = reverse("call-detail", kwargs={"sid": call.sid})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
