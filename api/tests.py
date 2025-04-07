import logging
import uuid
from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase, RequestsClient
from rest_framework_api_key.models import APIKey

from api.models import FlouciApp
from utils.api_keys_manager import ApiKeyServicesNames

client = RequestsClient()


def create_api_key(name):
    api_key, key = APIKey.objects.create_key(name=name)
    return key


class BaseCreateDeveloperApp(APITestCase):
    def setUp(self):
        self.name = "test"
        self.description = "test description"
        self.merchant_id = 1
        self.wallet = "rHDz3wJtYVvWfY9Xf97PFW8dUzUa85FZTc"
        self.username = uuid.uuid4()

        self.app = FlouciApp.objects.create(
            name="first app",
            description="first app",
            wallet=self.wallet,
            merchant_id=self.merchant_id,
            tracking_id=self.username,
            test=True,
        )
        self.api_key = create_api_key(ApiKeyServicesNames.BACKEND)
        self.data = {
            "name": self.name,
            "description": self.description,
            "merchant_id": self.merchant_id,
            "username": str(self.username),
            "wallet": self.wallet,
        }
        self.url = reverse("create_developer_app")


class TestCreateDeveloperApp(BaseCreateDeveloperApp):

    def setUp(self):
        super().setUp()
        self.api_key = create_api_key(ApiKeyServicesNames.BACKEND)
        self.data = {
            "name": self.name,
            "description": self.description,
            "merchant_id": self.merchant_id,
            "username": str(self.username),
            "wallet": self.wallet,
        }

        self.url = reverse("create_developer_app")

    def test_create_app_success(self):
        response = self.client.post(
            self.url,
            json=self.data,
            headers={"AUTHORIZATION": f"Api-Key {self.api_key}"},
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("name", response.json())

    def test_wrong_api_key(self):
        self.api_key = create_api_key("wrong name")
        response = self.client.post(
            self.url,
            json=self.data,
            headers={"AUTHORIZATION": f"Api-Key {self.api_key}"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "Authentication credentials were not provided.")

    def test_missing_required_field(self):
        incomplete_data = {
            "description": self.description,
            "merchant_id": self.merchant_id,
            "username": str(self.username),
            "wallet": self.wallet,
        }
        response = self.client.post(
            self.url,
            json=incomplete_data,
            headers={"AUTHORIZATION": f"Api-Key {self.api_key}"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.json())
        self.assertEqual(response.json()["name"][0], "This field is required.")

    def test_get_app_success(self):
        self.data = {
            "tracking_id": str(self.username),
        }
        response = self.client.get(
            self.url,
            params=self.data,
            headers={"AUTHORIZATION": f"Api-Key {self.api_key}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "developers")
        self.assertIsNotNone(response.json().get("result"))

    def test_get_app_missing_tracking_id(self):
        self.data = {}
        response = self.client.get(
            self.url,
            params=self.data,
            headers={"AUTHORIZATION": f"Api-Key {self.api_key}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("result"), [])

    def test_update_app_success(self):
        self.data = {
            "id": self.app.id,
            "name": "updated app",
            "description": "updated description",
        }
        response = self.client.put(
            self.url,
            data=self.data,
            headers={"AUTHORIZATION": f"Api-Key {self.api_key}"},
        )
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["name"], "updated app")
        self.assertEqual(data["description"], "updated description")

    def test_update_app_not_found(self):
        self.data = {
            "id": 9999,
            "name": "updated app",
            "description": "updated description",
        }
        response = self.client.put(
            self.url,
            data=self.data,
            headers={"AUTHORIZATION": f"Api-Key {self.api_key}"},
        )
        data = response.json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["detail"], "App not found.")

    def test_update_app_field_required(self):
        self.data = {
            "name": "updated app",
            "description": "updated description",
        }
        response = self.client.put(
            self.url,
            data=self.data,
            headers={"AUTHORIZATION": f"Api-Key {self.api_key}"},
        )
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["id"][0], "This field is required.")


class RevokeDeveloperAppViewTest(BaseCreateDeveloperApp):
    def setUp(self):
        super().setUp()
        self.api_key = create_api_key(ApiKeyServicesNames.BACKEND)

    def test_revoke_app_success(self):
        url = reverse("revoke_developer_app", kwargs={"id": self.app.id})

        response = self.client.get(
            url,
            headers={"AUTHORIZATION": f"Api-Key {self.api_key}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"]["id"], self.app.id)

    def test_revoke_app_not_found(self):
        non_existent_id = 99999
        url = reverse("revoke_developer_app", kwargs={"id": non_existent_id})

        response = self.client.get(
            url,
            headers={"AUTHORIZATION": f"Api-Key {self.api_key}"},
        )
        data = response.json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["detail"], "App not found.")


class TestGeneratePaymentView(BaseCreateDeveloperApp):
    def setUp(self):
        super().setUp()

        self.data = {
            "amount": 1000,
            "accept_card": True,
            "session_timeout_secs": 1200,
            "success_link": "https://example.com/success",
            "fail_link": "https://example.com/fail",
            "developer_tracking_id": str(uuid.uuid4()),
        }

        self.valid_headers = {"Authorization": f"Bearer {self.app.public_token}:{self.app.private_token}"}
        self.mock_generate_payment = {
            "success": True,
            "url": "https://flouci.test/pay/jvdqMbFKTAWQSrkeqlL1Rg",
            "payment_id": "jvdqMbFKTAWQSrkeqlL1Rg",
            "status_code": 200,
        }

    @patch("utils.backend_client.FlouciBackendClient.generate_payment_page")
    def test_generate_payment_success(self, mock_generate_payment):
        mock_generate_payment.return_value = self.mock_generate_payment
        response = self.client.post(
            reverse("generate_payment"),
            data=self.data,
            headers=self.valid_headers,
        )
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data["result"]["success"])
        self.assertEqual(response_data["result"]["payment_id"], "jvdqMbFKTAWQSrkeqlL1Rg")
        self.assertEqual(response_data["code"], 0)

    def test_invalid_token_format(self):
        headers = {"Authorization": "InvalidTokenFormat"}
        response = self.client.post(
            reverse("generate_payment"),
            data=self.data,
            headers=headers,
        )
        self.assertEqual(response.status_code, 403)

    def test_missing_authorization_header(self):
        response = self.client.post(
            reverse("generate_payment"),
            data=self.data,
        )
        self.assertEqual(response.status_code, 403)

    def test_invalid_app_credentials(self):
        headers = {"Authorization": "Bearer invalid_pub:invalid_priv"}
        response = self.client.post(
            reverse("generate_payment"),
            data=self.data,
            headers=headers,
        )
        self.assertEqual(response.status_code, 403)

    def test_amount_below_minimum(self):
        invalid_data = self.data.copy()
        invalid_data["amount"] = 50
        response = self.client.post(reverse("generate_payment"), data=invalid_data, headers=self.valid_headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("amount", response.json())

    @patch("utils.backend_client.FlouciBackendClient.generate_payment_page")
    def test_backend_failure(self, mock_generate_payment):
        mock_generate_payment.return_value = {
            "success": False,
            "result": "",
            "non_field_errors": ["Backend is down"],
            "status_code": 502,
        }

        response = self.client.post(reverse("generate_payment"), data=self.data, headers=self.valid_headers)
        self.assertEqual(response.status_code, 502)
        self.assertFalse(response.json()["result"]["success"])
        self.assertEqual(response.json()["code"], 1)

    def test_missing_required_field(self):
        invalid_data = self.data.copy()
        del invalid_data["success_link"]
        response = self.client.post(reverse("generate_payment"), data=invalid_data, headers=self.valid_headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("success_link", response.json())

    @patch("utils.backend_client.FlouciBackendClient.generate_payment_page")
    def test_with_destination(self, mock_generate_payment):
        mock_generate_payment.return_value = self.mock_generate_payment

        data_with_destination = self.data.copy()
        data_with_destination["destination"] = [
            {
                "destination": "2",
                "amount": 5000,
            },
            {
                "destination": "3",
                "amount": 5000,
            },
        ]

        response = self.client.post(
            reverse("generate_payment"),
            data=data_with_destination,
            headers=self.valid_headers,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["result"]["success"])
        self.assertEqual(response.json()["result"]["payment_id"], "jvdqMbFKTAWQSrkeqlL1Rg")

    @patch("utils.backend_client.FlouciBackendClient.generate_payment_page")
    def test_pre_authorization(self, mock_generate_payment):
        mock_generate_payment.return_value = self.mock_generate_payment

        data_with_preauth = self.data.copy()
        data_with_preauth["pre_authorization"] = True

        response = self.client.post(
            reverse("generate_payment"),
            data=data_with_preauth,
            headers=self.valid_headers,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["result"]["success"])
        self.assertEqual(response.json()["result"]["payment_id"], "jvdqMbFKTAWQSrkeqlL1Rg")


class TestVerifyPaymentView(BaseCreateDeveloperApp):
    def setUp(self):
        super().setUp()
        self.valid_headers = {"Authorization": f"Bearer {self.app.public_token}:{self.app.private_token}"}
        self.payment_id = "jvdqMbFKTAWQSrkeqlL1Rg"

    @patch("utils.backend_client.FlouciBackendClient.check_payment")
    def test_verify_payment_success(self, mock_check_payment):
        mock_check_payment.return_value = {
            "success": True,
            "result": {
                "type": "card",
                "amount": 7805000.0,
                "status": "SUCCESS",
                "details": {
                    "order_number": "I8kIPuPCRRaTzt3KzF7sfA",
                    "name": "aaa",
                    "pan": "450921**1119",
                    "payment_system": "VISA",
                    "expiration": "202612",
                    "approval_code": "199811",
                    "currency": "788",
                    "phone_number": "",
                    "email": "a@flouci.com",
                    "bank_country_code": "TN",
                    "destinations": [],
                },
                "developer_tracking_id": "70df906e-9a70-4007-9028-0b67318974cd",
                "status_code": 200,
            },
        }

        url = reverse("verify_payment", kwargs={"payment_id": self.payment_id})

        response = self.client.get(
            url,
            headers=self.valid_headers,
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["result"]["success"])
        self.assertEqual(data["result"]["payment_status"], "SUCCESS")

    @patch("utils.backend_client.FlouciBackendClient.check_payment")
    def test_verify_payment_failure(self, mock_check_payment):
        mock_check_payment.return_value = {"success": False, "result": "Invalid Transaction ID", "status_code": 200}
        url = reverse("verify_payment", kwargs={"payment_id": self.payment_id})
        response = self.client.get(
            url,
            headers=self.valid_headers,
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["result"]["success"])
        self.assertIn("Invalid Transaction ID", data["result"]["error"])

    def test_verify_payment_invalid_token_format(self):
        url = reverse("verify_payment", kwargs={"payment_id": self.payment_id})
        response = self.client.get(
            url,
            HTTP_AUTHORIZATION="InvalidToken",
        )
        self.assertEqual(response.status_code, 403)

    def test_verify_payment_missing_token(self):
        url = reverse("verify_payment", kwargs={"payment_id": self.payment_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)


class TestSendMoneyView(BaseCreateDeveloperApp):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.valid_headers = {"Authorization": f"Bearer {self.app.public_token}:{self.app.private_token}"}
        self.url = reverse("send_money")
        self.valid_data = {
            "amount": 1000,
            "destination": "12345",
            "webhook": "https://example.com/webhook",
        }

    @patch("utils.backend_client.FlouciBackendClient.developer_send_money_status")
    def test_send_money_success(self, mock_send_money):
        mock_send_money.return_value = {
            "success": True,
            "code": 0,
            "payment_id": "47fbe6be-9b9a-4060-84ad-cb69500d1865",
            "message": "Operation initiated successfully. You will receive a webhook with final confirmation.",
            "status_code": 200,
        }

        response = self.client.post(
            self.url,
            data=self.valid_data,
            headers=self.valid_headers,
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["result"]["success"])
        self.assertEqual(data["result"]["transaction_id"], "47fbe6be-9b9a-4060-84ad-cb69500d1865")
        self.assertEqual(
            data["result"]["message"],
            "Operation initiated successfully. You will receive a webhook with final confirmation.",
        )

    @patch("utils.backend_client.FlouciBackendClient.developer_send_money_status")
    def test_send_money_failure(self, mock_send_money):
        mock_send_money.return_value = {
            "success": False,
            "code": 4,
            "message": "Insufficient funds.",
            "status_code": 400,
        }

        response = self.client.post(
            self.url,
            data=self.valid_data,
            headers=self.valid_headers,
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["result"]["success"])
        self.assertEqual(data["result"]["error"], "Insufficient funds.")
        self.assertEqual(data["result"]["code"], 4)

    @patch("utils.backend_client.FlouciBackendClient.developer_send_money_status")
    def test_send_money_missing_required_field(self, mock_send_money):
        invalid_data = self.valid_data.copy()
        del invalid_data["amount"]

        response = self.client.post(
            self.url,
            data=invalid_data,
            headers=self.valid_headers,
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("amount", response.json())

    @patch("utils.backend_client.FlouciBackendClient.developer_send_money_status")
    def test_send_money_invalid_amount(self, mock_send_money):
        invalid_data = self.valid_data.copy()
        invalid_data["amount"] = 50

        response = self.client.post(
            self.url,
            data=invalid_data,
            headers=self.valid_headers,
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("amount", response.json())

    def test_unauthorized_access(self):
        response = self.client.post(self.url, data=self.valid_data, headers={"Authorization": "Bearer invalidtoken"})

        self.assertEqual(response.status_code, 403)

    @patch("utils.backend_client.FlouciBackendClient.developer_send_money_status")
    def test_send_money_without_webhook(self, mock_send_money):
        data_without_webhook = {
            "amount": 1000,
            "destination": "12345",
        }

        mock_send_money.return_value = {
            "success": True,
            "message": "Transaction successful",
            "payment_id": "jvdqMbFKTAWQSrkeqlL1Rg",
            "status_code": 200,
        }

        response = self.client.post(
            self.url,
            data=data_without_webhook,
            headers=self.valid_headers,
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["result"]["success"])
        self.assertEqual(data["result"]["transaction_id"], "jvdqMbFKTAWQSrkeqlL1Rg")
        self.assertEqual(data["result"]["message"], "Transaction successful")

    def test_send_money_invalid_token(self):
        response = self.client.post(self.url, data=self.valid_data, headers={"Authorization": "Bearer invalid_token"})

        self.assertEqual(response.status_code, 403)

    @patch("utils.backend_client.FlouciBackendClient.developer_send_money_status")
    def test_send_money_invalid_reciver(self, mock_send_money):
        mock_send_money.return_value = {
            "success": False,
            "code": 1,
            "message": "User does not exist.",
            "status_code": 404,
        }

        invalid_data = self.valid_data.copy()

        response = self.client.post(
            self.url,
            data=invalid_data,
            headers=self.valid_headers,
        )

        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertFalse(data["result"]["success"])
        self.assertEqual(data["result"]["error"], "User does not exist.")
        self.assertEqual(data["result"]["code"], 1)


class TestCheckSendMoneyStatusView(BaseCreateDeveloperApp):
    def setUp(self):
        self.client = APIClient()
        super().setUp()
        self.valid_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.app.public_token}:{self.app.private_token}"}
        self.operation_id = uuid.uuid4()
        self.url = reverse("check_payment_status", kwargs={"operation_id": self.operation_id})

    @patch("utils.backend_client.FlouciBackendClient.developer_check_send_money_status")
    def test_check_payment_status_success(self, mock_backend):
        mock_backend.return_value = {
            "success": True,
            "result": {
                "operation_type": "DEVELOPER_API",
                "amount": 100.0,
                "status": "SUCCESS",
                "details": {
                    "payment_id": self.operation_id,
                    "webhook_url": None,
                    "webhook_sent": False,
                    "transaction_type": "MERCHANT",
                    "destination": "20",
                    "time_created": "2025-03-12T10:38:28.448977Z",
                    "description": "",
                },
            },
            "status_code": 200,
        }

        response = self.client.get(self.url, **self.valid_headers)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["result"]["success"])
        self.assertEqual(data["result"]["transaction_status"], "SUCCESS")
        self.assertEqual(data["result"]["transaction_id"], str(self.operation_id))

    @patch("utils.backend_client.FlouciBackendClient.developer_check_send_money_status")
    def test_check_payment_status_backend_failure(self, mock_backend):
        mock_backend.return_value = {
            "success": False,
            "message": "Transaction not found",
            "code": 404,
            "status_code": 404,
        }

        response = self.client.get(self.url, **self.valid_headers)

        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertFalse(data["result"]["success"])
        self.assertEqual(data["result"]["message"], "Transaction not found")
        self.assertEqual(data["result"]["code"], 404)

    def test_check_payment_status_invalid_token_format(self):
        response = self.client.get(self.url, HTTP_AUTHORIZATION="InvalidToken")
        self.assertEqual(response.status_code, 403)

    def test_check_payment_status_missing_token(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    @patch("utils.backend_client.FlouciBackendClient.developer_check_send_money_status")
    def test_check_payment_status_user_not_allowed(self, mock_backend):
        mock_backend.return_value = {"success": False, "result": "Not allowed.", "status_code": 406}
        response = self.client.get(self.url, **self.valid_headers)

        self.assertEqual(response.status_code, 406)
        data = response.json()
        logging.info(f"data {data}")
        self.assertFalse(data["result"]["success"])
        self.assertEqual(data["result"]["result"], "Not allowed.")


class TestCheckUserExistsView(BaseCreateDeveloperApp):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.invalid_tracking_id = uuid.uuid4()

        self.api_key = create_api_key(ApiKeyServicesNames.BACKEND)
        self.valid_headers = {"Authorization": f"Api-Key {self.api_key}"}

    def test_user_exists_success(self):
        url = reverse("check_user_exists", kwargs={"tracking_id": self.app.tracking_id})
        response = self.client.get(url, headers=self.valid_headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

    def test_user_does_not_exist(self):
        url = reverse("check_user_exists", kwargs={"tracking_id": str(self.invalid_tracking_id)})
        response = self.client.get(url, headers=self.valid_headers)
        self.assertEqual(response.status_code, 412)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["result"]["message"], "User has no developer account")

    def test_invalid_uuid_format(self):
        with self.assertRaises(Exception):
            reverse("check_user_exists", kwargs={"tracking_id": "not-a-uuid"})

    def test_missing_auth(self):
        url = reverse("check_user_exists", kwargs={"tracking_id": self.app.tracking_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)


class TestCreateDeveloperAccountView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.api_key = create_api_key(ApiKeyServicesNames.BACKEND)
        self.valid_headers = {"Authorization": f"Api-Key {self.api_key}"}
        self.url = reverse("create_developer_account")

    def test_create_developer_account_success(self):
        login_id = str(uuid.uuid4())
        response = self.client.post(self.url, {"login": login_id}, headers=self.valid_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["result"], "account_created")
        self.assertTrue(FlouciApp.objects.filter(tracking_id=login_id).exists())

    def test_create_developer_account_already_exists(self):
        existing_login = str(uuid.uuid4())
        FlouciApp.objects.create(
            name="Existing App",
            description="Already exists",
            wallet="rHDz3wJtYVvWfY9Xf97PFW8dUzUa85FZTc",
            merchant_id=123,
            tracking_id=existing_login,
            test=True,
        )
        response = self.client.post(self.url, {"login": existing_login}, headers=self.valid_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_412_PRECONDITION_FAILED)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "User exists.")

    def test_create_developer_account_invalid_login_field(self):
        response = self.client.post(self.url, {"invalid": "data"}, headers=self.valid_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("login", response.data)

    def test_create_developer_account_unauthorized(self):
        response = self.client.post(self.url, {"login": str(uuid.uuid4())}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestDisableDeveloperAppView(BaseCreateDeveloperApp):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.api_key = create_api_key(ApiKeyServicesNames.BACKEND)
        self.valid_headers = {"Authorization": f"Api-Key {self.api_key}"}

        self.url = reverse("enable_developer_app", kwargs={"id": self.app.id})
        self.nonexistent_url = reverse("enable_developer_app", kwargs={"id": 9999})

    def test_disable_app_success(self):
        response = self.client.get(self.url, headers=self.valid_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "App disabled successfully.")
        self.app.refresh_from_db()
        self.assertFalse(self.app.active)

    def test_disable_app_not_found(self):
        response = self.client.get(self.nonexistent_url, headers=self.valid_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "App not found.")

    def test_disable_app_unauthorized(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_disable_app_invalid_id(self):
        invalid_url = "/api/app/abc/disable"
        response = self.client.get(invalid_url, headers=self.valid_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestEnableDeveloperAppView(BaseCreateDeveloperApp):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.api_key = create_api_key(ApiKeyServicesNames.BACKEND)
        self.valid_headers = {"Authorization": f"Api-Key {self.api_key}"}

        self.url = reverse("disable_developer_app", kwargs={"id": self.app.id})
        self.nonexistent_url = reverse("disable_developer_app", kwargs={"id": 9999})

    def test_enable_app_success(self):
        response = self.client.get(self.url, headers=self.valid_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "App enabled successfully.")
        self.app.refresh_from_db()
        self.assertTrue(self.app.active)

    def test_enable_app_not_found(self):
        response = self.client.get(self.nonexistent_url, headers=self.valid_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "App not found.")

    def test_enable_app_unauthorized(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_enable_app_invalid_id(self):
        invalid_url = "/api/app/abc/enable"
        response = self.client.get(invalid_url, headers=self.valid_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestAcceptPaymentView(BaseCreateDeveloperApp):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.valid_headers = {"Authorization": f"Bearer {self.app.public_token}:{self.app.private_token}"}
        self.url = reverse("accept_payment")

    def test_accept_payment_success_test_mode(self):
        data = {
            "flouci_otp": "F-111111",
            "payment_id": "pmt-123",
            "amount": 1000,
        }
        response = self.client.post(self.url, data, headers=self.valid_headers, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"]["status"], "SUCCESS")

    def test_accept_payment_failure_test_mode(self):
        data = {
            "flouci_otp": "F-000000",
            "payment_id": "pmt-123",
            "amount": 1000,
        }
        response = self.client.post(self.url, data, headers=self.valid_headers, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"]["status"], "FAILED")

    def test_accept_payment_missing_fields(self):
        data = {
            "amount": 1000,
        }
        response = self.client.post(self.url, data, headers=self.valid_headers, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("flouci_otp", response.data)
        self.assertIn("payment_id", response.data)


class TestGeneratePaymentWordpressView(BaseCreateDeveloperApp):
    def setUp(self):
        super().setUp()
        self.client = APIClient()

        self.valid_headers = {"Authorization": f"Bearer {self.app.public_token}:{self.app.private_token}"}

        self.valid_payload = {
            "amount": 1000,
            "accept_card": True,
            "session_timeout_secs": 1200,
            "session_timeout": 1200,
            "success_link": "https://example.com/success",
            "fail_link": "https://example.com/fail",
            "developer_tracking_id": str(self.app.tracking_id),
            "accept_edinar": True,
            "currency": "TND",
            "webhook": "https://example.com/webhook",
            "destination": [],
            "pre_authorization": False,
        }

        self.url = reverse("generate_payment_wordpress")

    @patch("utils.backend_client.FlouciBackendClient.generate_payment_page")
    def test_generate_payment_success(self, mock_generate_payment):
        mock_generate_payment.return_value = {
            "success": True,
            "url": "https://flouci.test/pay/jvdqMbFKTAWQSrkeqlL1Rg",
            "payment_id": "jvdqMbFKTAWQSrkeqlL1Rg",
            "developer_tracking_id": str(self.app.tracking_id),
            "status_code": 200,
        }

        response = self.client.post(self.url, data=self.valid_payload, format="json", headers=self.valid_headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["result"]["success"])
        self.assertEqual(response.data["result"]["link"], "https://flouci.test/pay/jvdqMbFKTAWQSrkeqlL1Rg")
        self.assertEqual(response.data["code"], 0)

    @patch("utils.backend_client.FlouciBackendClient.generate_payment_page")
    def test_generate_payment_failure(self, mock_generate_payment):
        mock_generate_payment.return_value = {
            "success": False,
            "result": "Invalid merchant ID",
            "non_field_errors": ["Merchant not authorized"],
            "status_code": 400,
        }

        response = self.client.post(self.url, data=self.valid_payload, format="json", headers=self.valid_headers)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data["result"]["success"])
        self.assertEqual(response.data["code"], 1)
        self.assertIn("error", response.data["result"])

    def test_generate_payment_unauthorized(self):
        response = self.client.post(self.url, data=self.valid_payload, format="json")
        self.assertEqual(response.status_code, 403)
