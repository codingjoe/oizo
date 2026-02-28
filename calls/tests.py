from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Call


class CallModelTest(TestCase):
    def test_str(self):
        call = Call(
            sid="00000000-0000-0000-0000-000000000001", status=Call.Status.QUEUED
        )
        self.assertIn("queued", str(call))

    def test_default_status(self):
        call = Call(from_number="+15551234567", to_number="+15559876543")
        self.assertEqual(call.status, Call.Status.QUEUED)

    def test_default_direction(self):
        call = Call(from_number="+15551234567", to_number="+15559876543")
        self.assertEqual(call.direction, Call.Direction.OUTBOUND_API)


class CallAPITest(APITestCase):
    def _create_call(self, **kwargs):
        defaults = {
            "from_number": "+15551234567",
            "to_number": "+15559876543",
            "url": "https://example.com/twiml",
        }
        defaults.update(kwargs)
        return Call.objects.create(**defaults)

    def test_list_calls(self):
        self._create_call()
        url = reverse("call-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_create_call(self):
        url = reverse("call-list")
        data = {
            "from_number": "+15551234567",
            "to_number": "+15559876543",
            "url": "https://example.com/twiml",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("sid", response.data)
        self.assertEqual(response.data["from_number"], data["from_number"])

    def test_retrieve_call(self):
        call = self._create_call()
        url = reverse("call-detail", kwargs={"sid": call.sid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data["sid"]), str(call.sid))

    def test_cancel_queued_call(self):
        call = self._create_call()
        self.assertEqual(call.status, Call.Status.QUEUED)
        url = reverse("call-detail", kwargs={"sid": call.sid})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        call.refresh_from_db()
        self.assertEqual(call.status, Call.Status.CANCELED)

    def test_cancel_completed_call_returns_conflict(self):
        call = self._create_call()
        call.status = Call.Status.COMPLETED
        call.save()
        url = reverse("call-detail", kwargs={"sid": call.sid})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_update_call_url(self):
        call = self._create_call()
        url = reverse("call-detail", kwargs={"sid": call.sid})
        new_url = "https://example.com/new-twiml"
        response = self.client.patch(url, {"url": new_url}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        call.refresh_from_db()
        self.assertEqual(call.url, new_url)
