from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_api_key.models import APIKey

from utils.api_keys_manager import ApiKeyServicesNames


class TestApiKeysPermission(APITestCase):
    def setUp(self):
        self.service1_client = APIClient()
        self.service1_client.credentials(
            HTTP_AUTHORIZATION=f"Api-Key {APIKey.objects.create_key(name=ApiKeyServicesNames.SERVICE1)[1]}"
        )
        self.service2_client = APIClient()
        self.service2_client.credentials(
            HTTP_AUTHORIZATION="Api-Key "
            f"{APIKey.objects.create_key(name=ApiKeyServicesNames.SERVICE2+'random_suffix')[1]}"
        )

    def test_name_based_api_key(self):
        response = self.service1_client.get(reverse("service1"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_start_with_based_api_key(self):
        response = self.service2_client.get(reverse("service2"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_wrong_api_key(self):
        response = self.service1_client.get(reverse("service2"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
