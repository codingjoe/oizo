from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import PhoneNumber


class PhoneNumberModelTest(TestCase):
    def test_str(self):
        number = PhoneNumber(phone_number="+4930123456789")
        self.assertEqual(str(number), "+4930123456789")

    def test_default_status(self):
        number = PhoneNumber(phone_number="+4930123456789")
        self.assertEqual(number.status, PhoneNumber.Status.ACTIVE)


class PhoneNumberAPITest(APITestCase):
    def _create_number(self, **kwargs):
        defaults = {"phone_number": "+4930123456789", "iso_country": "DE"}
        defaults.update(kwargs)
        return PhoneNumber.objects.create(**defaults)

    def test_list_numbers(self):
        self._create_number()
        url = reverse("phonenumber-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_create_number(self):
        url = reverse("phonenumber-list")
        data = {"phone_number": "+4930000000001", "iso_country": "DE"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("sid", response.data)

    def test_retrieve_number(self):
        number = self._create_number()
        url = reverse("phonenumber-detail", kwargs={"sid": number.sid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["phone_number"], number.phone_number)

    def test_update_voice_url(self):
        number = self._create_number()
        url = reverse("phonenumber-detail", kwargs={"sid": number.sid})
        new_url = "https://example.com/inbound"
        response = self.client.patch(url, {"voice_url": new_url}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        number.refresh_from_db()
        self.assertEqual(number.voice_url, new_url)

    def test_delete_number(self):
        number = self._create_number()
        url = reverse("phonenumber-detail", kwargs={"sid": number.sid})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
