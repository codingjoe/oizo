from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Trunk


class TrunkModelTest(TestCase):
    def test_str(self):
        trunk = Trunk(friendly_name="My Trunk", domain_name="trunk.example.com")
        self.assertIn("My Trunk", str(trunk))
        self.assertIn("trunk.example.com", str(trunk))


class TrunkAPITest(APITestCase):
    def _create_trunk(self, **kwargs):
        defaults = {"friendly_name": "Test Trunk", "domain_name": "trunk.example.com"}
        defaults.update(kwargs)
        return Trunk.objects.create(**defaults)

    def test_list_trunks(self):
        self._create_trunk()
        url = reverse("trunk-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_create_trunk(self):
        url = reverse("trunk-list")
        data = {"friendly_name": "My SIP Trunk", "domain_name": "my-trunk.example.com"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("sid", response.data)
        self.assertEqual(response.data["domain_name"], data["domain_name"])

    def test_retrieve_trunk(self):
        trunk = self._create_trunk()
        url = reverse("trunk-detail", kwargs={"sid": trunk.sid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["friendly_name"], trunk.friendly_name)

    def test_update_trunk(self):
        trunk = self._create_trunk()
        url = reverse("trunk-detail", kwargs={"sid": trunk.sid})
        response = self.client.patch(
            url, {"friendly_name": "Updated Trunk"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        trunk.refresh_from_db()
        self.assertEqual(trunk.friendly_name, "Updated Trunk")

    def test_delete_trunk(self):
        trunk = self._create_trunk()
        url = reverse("trunk-detail", kwargs={"sid": trunk.sid})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Trunk.objects.filter(pk=trunk.pk).exists())

    def test_duplicate_domain_name_rejected(self):
        self._create_trunk()
        url = reverse("trunk-list")
        data = {"friendly_name": "Another Trunk", "domain_name": "trunk.example.com"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
