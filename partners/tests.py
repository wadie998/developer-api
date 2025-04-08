import uuid
from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase

from api.enum import RequestStatus, SendMoneyServiceOperationTypes
from api.models import FlouciApp
from partners.models import LinkedAccount, PartnerTransaction


class BaseCreateDeveloperApp(APITestCase):
    def setUp(self):
        self.phone_number = "22222222"

        self.app = FlouciApp.objects.create(
            name="Partner App",
            wallet="rHDz3wJtYVvWfY9Xf97PFW8dUzUa85FZTc",
            merchant_id=111,
            tracking_id=uuid.uuid4(),
            has_partner_access=True,
            test=True,
        )
        self.public_token = str(uuid.uuid4())
        self.private_token = str(uuid.uuid4())
        self.app.public_token = self.public_token
        self.app.private_token = self.private_token
        self.app.save()


class InitiateLinkAccountViewTest(BaseCreateDeveloperApp):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.url = reverse("partner_initiate_link_account")
        self.valid_headers = {"Authorization": f"Bearer {self.public_token}:{self.private_token}"}
        self.valid_payload = {"phone_number": self.phone_number}

    def create_linked_account(self, phone_number, tracking_id):
        return LinkedAccount.objects.create(
            phone_number=phone_number,
            account_tracking_id=tracking_id,
            merchant_id=111,
        )

    @patch("utils.backend_client.FlouciBackendClient.initiate_link_account")
    def test_phone_number_not_exists(self, mock_backend):
        mock_backend.return_value = {"success": False, "message": "Error.", "status_code": 404}
        res = self.client.post(
            self.url,
            data={"phone_number": "12345678"},
            headers=self.valid_headers,
            format="json",
        )
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.data["message"], "Unexpected error occurred")

    @patch("utils.backend_client.FlouciBackendClient.initiate_link_account")
    def test_200_success_link(self, mock_backend):
        phone_number = "99142989"
        mock_backend.return_value = {
            "success": True,
            "message": "Verification code is sent to: 99142989",
            "body": {
                "phone_number": "99142989",
                "name": "Anis",
                "session_id": "15099b80-335f-4a38-9f86-587972eaaf69",
                "tracking_id": "e8270859-e944-47cd-8df0-cd6eb5fe002f",
            },
            "status_code": 200,
        }
        self.create_linked_account(phone_number=phone_number, tracking_id=str(uuid.uuid4()))

        res = self.client.post(self.url, self.valid_payload, format="json", headers=self.valid_headers)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data["success"])
        self.assertEqual(res.data["phone_number"], phone_number)

    @patch("utils.backend_client.FlouciBackendClient.initiate_link_account")
    def test_412_account_not_compatible(self, mock_backend):
        mock_backend.return_value = {"success": False, "status_code": 412, "message": "Account not compatible"}
        res = self.client.post(self.url, self.valid_payload, format="json", headers=self.valid_headers)
        self.assertEqual(res.status_code, 412)
        self.assertFalse(res.data["success"])

    def test_202_already_linked_by_tracking_id(self):
        tracking_id = str(uuid.uuid4())
        self.create_linked_account(phone_number=self.phone_number, tracking_id=tracking_id)
        data = {"phone_number": self.phone_number}
        res = self.client.post(self.url, data, format="json", headers=self.valid_headers)
        self.assertEqual(res.status_code, 202)
        self.assertFalse(res.data["success"])
        self.assertIn("Account already linked", res.data["message"])

    @patch("utils.backend_client.FlouciBackendClient.initiate_link_account")
    def test_429_too_many_sms(self, mock_backend):
        mock_backend.return_value = {
            "success": False,
            "message": "Too many sms sent, try again later",
            "body": {"phone_number": "99142989"},
            "status_code": 429,
        }
        res = self.client.post(self.url, self.valid_payload, format="json", headers=self.valid_headers)
        self.assertEqual(res.status_code, 429)
        self.assertFalse(res.data["success"])

    def test_401_unauthorized_missing_token(self):
        res = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(res.status_code, 403)


class TestConfirmLinkAccountView(BaseCreateDeveloperApp):
    def setUp(self):
        super().setUp()
        self.url = reverse("partner_confirm_link_account")
        self.headers = {"Authorization": f"Bearer {self.public_token}:{self.private_token}"}
        self.valid_data = {
            "phone_number": "12345678",
            "session_id": str(uuid.uuid4()),
            "otp": "123456",
        }

    @patch("utils.backend_client.FlouciBackendClient.confirm_link_account")
    def test_successful_link(self, mock_confirm):
        mock_confirm.return_value = {
            "success": True,
            "phone_number": "99142989",
            "session_id": "15099b80-335f-4a38-9f86-587972eaaf69",
            "tracking_id": "e8270859-e944-47cd-8df0-cd6eb5fe002f",
            "message": "Account Linking Authorized",
            "status_code": 200,
        }
        response = self.client.post(self.url, data=self.valid_data, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get("success"))
        self.assertIn("tracking_id", response.data)

    @patch("utils.backend_client.FlouciBackendClient.confirm_link_account")
    def test_expired_otp(self, mock_confirm):
        mock_confirm.return_value = {
            "success": False,
            "message": "Invalid Code, please try again 1",
            "status_code": 401,
        }
        response = self.client.post(self.url, data=self.valid_data, headers=self.headers)
        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.data.get("success"))
        self.assertEqual(response.data.get("message"), "Invalid Code, please try again 1")

    @patch("utils.backend_client.FlouciBackendClient.confirm_link_account")
    def test_wrong_otp(self, mock_confirm):
        mock_confirm.return_value = {
            "success": False,
            "message": "Invalid Code, please try again 2",
            "status_code": 406,
        }
        response = self.client.post(self.url, data=self.valid_data, headers=self.headers)
        self.assertEqual(response.status_code, 406)
        self.assertFalse(response.data.get("success"))
        self.assertEqual(response.data.get("message"), "Invalid Code, please try again 2")


class TestIsFlouciView(BaseCreateDeveloperApp):
    def setUp(self):
        super().setUp()
        self.url = reverse("is_flouci")
        self.valid_headers = {"Authorization": f"Bearer {self.public_token}:{self.private_token}"}
        self.valid_data = {
            "phone_number": self.phone_number,
        }

    @patch("utils.backend_client.FlouciBackendClient.is_flouci")
    def test_user_is_flouci(self, mock_is_flouci):
        mock_is_flouci.return_value = {
            "success": True,
            "is_flouci": True,
            "status_code": 200,
        }
        response = self.client.post(self.url, data=self.valid_data, headers=self.valid_headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get("success"))
        self.assertTrue(response.data.get("is_flouci"))

    @patch("utils.backend_client.FlouciBackendClient.is_flouci")
    def test_user_is_not_flouci(self, mock_is_flouci):
        mock_is_flouci.return_value = {
            "success": True,
            "is_flouci": False,
            "status_code": 200,
        }
        response = self.client.post(self.url, data=self.valid_data, headers=self.valid_headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get("success"))
        self.assertFalse(response.data.get("is_flouci"))

    @patch("utils.backend_client.FlouciBackendClient.is_flouci")
    def test_phone_number_not_exist(self, mock_is_flouci):
        mock_is_flouci.return_value = {
            "success": True,
            "is_flouci": False,
            "status_code": 200,
        }
        response = self.client.post(self.url, data=self.valid_data, headers=self.valid_headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get("success"))
        self.assertFalse(response.data.get("is_flouci"))

    def test_invalid_phone_number_format(self):
        invalid_data = {
            "phone_number": "123",
        }
        response = self.client.post(self.url, data=invalid_data, headers=self.valid_headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("phone_number", response.data)


class TestAuthenticateView(BaseCreateDeveloperApp):
    def setUp(self):
        super().setUp()
        self.url = reverse("partner_authenticate")
        self.valid_headers = {"Authorization": f"Bearer {self.public_token}:{self.private_token}"}
        self.valid_data = {
            "phone_number": self.phone_number,
        }
        self.linked_account = LinkedAccount.objects.create(
            partner_tracking_id=uuid.uuid4(),
            account_tracking_id=uuid.uuid4(),
            merchant_id=self.app.merchant_id,
            phone_number=self.phone_number,
        )

    @patch("utils.backend_client.FlouciBackendClient.generate_authentication_token")
    def test_authenticate_success(self, mock_generate_token):
        mock_generate_token.return_value = {
            "success": True,
            "type": "I",
            "token": "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDQwNjA2OTcsImlhdCI6MTc0NDA1OTc5NywicGFydG5"
            "lcl90cmFja2luZ19pZCI6IjE1MDk5YjgwLTMzNWYtNGEzOC05Zjg2LTU4Nzk3MmVhYWY2MCIsIm1pZCI6IjIxIiwidHlwZSI6InBh"
            "cnRuZXIifQ.LPMtxeGgD1b3Htb-vlSBGzH0sDk2lmBaP0RDYCbSJoGJAEUvtFT3OeQE5kpiM_73UEKwyC7pR19FcRxiYHD6Fw",
            "refresh_token": "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDQwNjMzOTcsImlhdCI6MTc0NDA1OTc5Ny"
            "wicGFydG5lcl90cmFja2luZ19pZCI6IjE1MDk5YjgwLTMzNWYtNGEzOC05Zjg2LTU4Nzk3MmVhYWY2MCIsIm1pZCI6IjIxIiwidH"
            "lwZSI6InJlZnJlc2gifQ.yFhztUhvfrZUcFvcUe-yL7Cxj-HI0ANfUNdUUCxw3VXd6VjZteBB5Xm1tVTZF2V7ph5P5StoARFGVt2"
            "BXnLF0g",
            "status_code": 200,
        }
        data = {
            "phone_number": self.linked_account.phone_number,
            "tracking_id": self.linked_account.partner_tracking_id,
        }
        response = self.client.post(self.url, data=data, headers=self.valid_headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get("success"))
        self.assertEqual(
            response.data.get("token"),
            "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDQwNjA2OTcsImlhdCI6MTc0NDA1OTc5NywicGFydG5lcl90cm"
            "Fja2luZ19pZCI6IjE1MDk5YjgwLTMzNWYtNGEzOC05Zjg2LTU4Nzk3MmVhYWY2MCIsIm1pZCI6IjIxIiwidHlwZSI6InBhcnRuZ"
            "XIifQ.LPMtxeGgD1b3Htb-vlSBGzH0sDk2lmBaP0RDYCbSJoGJAEUvtFT3OeQE5kpiM_73UEKwyC7pR19FcRxiYHD6Fw",
        )

    @patch("utils.backend_client.FlouciBackendClient.generate_authentication_token")
    def test_authenticate_success_mrtchant_not_ppa(self, mock_generate_token):
        mock_generate_token.return_value = {
            "success": False,
            "type": "M",
            "is_ppa": False,
            "status_code": 412,
        }

        data = {
            "phone_number": self.linked_account.phone_number,
            "tracking_id": self.linked_account.partner_tracking_id,
        }

        response = self.client.post(self.url, data=data, headers=self.valid_headers)

        self.assertEqual(response.status_code, 412)
        self.assertFalse(response.data.get("success"))
        self.assertEqual(response.data.get("is_ppa"), False)

    @patch("utils.backend_client.FlouciBackendClient.generate_authentication_token")
    def test_linked_account_not_found(self, mock_generate_token):
        mock_generate_token.return_value = {
            "success": False,
            "status_code": 412,
        }
        data = {
            "phone_number": self.phone_number,
            "tracking_id": str(uuid.uuid4()),
        }

        response = self.client.post(self.url, data=data, headers=self.valid_headers)

        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.data.get("success"))
        self.assertEqual(response.data.get("message"), "Unauthorized")

    def test_invalid_phone_number(self):
        data = {
            "phone_number": "abc123",
            "tracking_id": self.linked_account.partner_tracking_id,
        }

        response = self.client.post(self.url, data=data, headers=self.valid_headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("phone_number", response.data)


class TestRefreshAuthenticateView(BaseCreateDeveloperApp):
    def setUp(self):
        super().setUp()
        self.url = reverse("partner_refresh_authenticate")
        self.partner_tracking_id = str(uuid.uuid4())
        self.account_tracking_id = str(uuid.uuid4())
        self.merchant_id = 111
        self.linked_account = LinkedAccount.objects.create(
            phone_number="12345678",
            partner_tracking_id=self.partner_tracking_id,
            account_tracking_id=self.account_tracking_id,
            merchant_id=self.merchant_id,
        )
        self.token = f"{self.app.public_token}:{self.app.private_token}"
        self.valid_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}


class TestPartnerBalanceView(BaseCreateDeveloperApp):
    def setUp(self):
        super().setUp()
        self.url = reverse("v1_partner_balance")
        self.partner_tracking_id = str(uuid.uuid4())
        self.account_tracking_id = str(uuid.uuid4())
        self.merchant_id = 111
        self.token = f"{self.app.public_token}:{self.app.private_token}"
        self.valid_headers = {"Authorization": f"Bearer {self.token}"}
        self.linked_account = LinkedAccount.objects.create(
            phone_number=self.phone_number,
            partner_tracking_id=self.partner_tracking_id,
            account_tracking_id=self.account_tracking_id,
            merchant_id=self.merchant_id,
        )

    @patch("utils.backend_client.FlouciBackendClient.get_user_balance")
    def test_balance_success(self, mock_get_balance):
        mock_get_balance.return_value = {
            "success": True,
            "balance": 1000,
            "status_code": 200,
        }

        param = {
            "phone_number": self.phone_number,
            "tracking_id": self.partner_tracking_id,
        }

        response = self.client.get(self.url, data=param, headers=self.valid_headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get("success"))
        self.assertEqual(response.data.get("balance"), 1000)

    @patch("utils.backend_client.FlouciBackendClient.get_user_balance")
    def test_missing_parameters(self, mock_get_balance):
        mock_get_balance.return_value = {
            "success": True,
            "balance": 1000,
            "status_code": 200,
        }

        param = {"tracking_id": self.partner_tracking_id}
        response = self.client.get(self.url, data=param, headers=self.valid_headers)
        self.assertEqual(response.status_code, 403)

        param = {"phone_number": self.phone_number}
        response = self.client.get(self.url, data=param, headers=self.valid_headers)
        self.assertEqual(response.status_code, 403)

    @patch("utils.backend_client.FlouciBackendClient.get_user_balance")
    def test_invalid_linked_account(self, mock_get_balance):
        mock_get_balance.return_value = {
            "success": True,
            "balance": 1000,
            "status_code": 200,
        }

        param = {"phone_number": "2543", "tracking_id": self.partner_tracking_id}
        response = self.client.get(self.url, data=param, headers=self.valid_headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["message"], "Invalid credentials")

    @patch("utils.backend_client.FlouciBackendClient.get_user_balance")
    def test_invalid_authorization_token(self, mock_get_balance):
        mock_get_balance.return_value = {
            "success": True,
            "balance": 1000,
            "status_code": 200,
        }

        invalid_token = "Bearer invalid_token"
        headers = {"Authorization": invalid_token}
        param = {"phone_number": self.phone_number, "tracking_id": self.partner_tracking_id}
        response = self.client.get(self.url, data=param, **headers)
        self.assertEqual(response.status_code, 403)


class TestPartnerHistoryView(BaseCreateDeveloperApp):
    def setUp(self):
        super().setUp()
        self.url = reverse("v1_partner_history")
        self.linked_account = LinkedAccount.objects.create(
            phone_number=self.phone_number,
            partner_tracking_id=self.app.tracking_id,
            merchant_id=self.app.merchant_id,
            account_tracking_id=self.app.tracking_id,
        )
        self.token = f"{self.app.public_token}:{self.app.private_token}"
        self.valid_headers = {"Authorization": f"Bearer {self.token}"}

    def test_history_empty_results(self):
        param = {
            "phone_number": self.phone_number,
            "tracking_id": self.app.tracking_id,
        }
        response = self.client.get(self.url, param, headers=self.valid_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"], [])
        self.assertEqual(response.data["count"], 0)

    def test_history_success(self):
        param = {
            "phone_number": self.phone_number,
            "tracking_id": self.app.tracking_id,
        }
        PartnerTransaction.objects.create(
            operation_type=SendMoneyServiceOperationTypes.P2P,
            sender=self.linked_account,
            receiver=self.linked_account,
            amount_in_millimes=100000,
            operation_payload={"amount": 100.0},
            operation_status=RequestStatus.APPROVED,
        )
        response = self.client.get(self.url, param, headers=self.valid_headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data["results"])
        self.assertEqual(response.data["count"], 1)

    def test_history_missing_authorization(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_history_invalid_phone_number(self):
        param = {
            "phone_number": "invalid_phone_number",
            "tracking_id": str(self.app.tracking_id),
        }

        response = self.client.get(self.url, param, headers=self.valid_headers)
        self.assertEqual(response.status_code, 403)

    def test_history_invalid_tracking_id(self):
        param = {
            "phone_number": self.phone_number,
            "tracking_id": str(uuid.uuid4()),
        }

        response = self.client.get(self.url, param, headers=self.valid_headers)
        self.assertEqual(response.status_code, 403)

    def test_history_empty_results_no_transactions(self):
        param = {
            "phone_number": self.phone_number,
            "tracking_id": self.app.tracking_id,
        }

        PartnerTransaction.objects.all().delete()

        response = self.client.get(self.url, param, headers=self.valid_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"], [])
        self.assertEqual(response.data["count"], 0)

    def test_history_date_range_filter(self):
        param = {
            "phone_number": self.phone_number,
            "tracking_id": str(self.app.tracking_id),
            "from": "2025-04-01T00:00:00Z",
            "to": "2025-04-07T23:59:59Z",
        }

        PartnerTransaction.objects.create(
            sender=self.linked_account,
            receiver=self.linked_account,
            operation_id=str(uuid.uuid4()),
            time_created=timezone.now(),
            operation_payload={},
            operation_type=SendMoneyServiceOperationTypes.P2P,
            amount_in_millimes=1020,
            operation_status=RequestStatus.APPROVED,
        )

        response = self.client.get(self.url, param, headers=self.valid_headers)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data["results"]), 0)

    def test_history_invalid_size(self):
        param = {
            "phone_number": self.phone_number,
            "tracking_id": str(self.app.tracking_id),
            "size": 10001,
        }

        response = self.client.get(self.url, param, headers=self.valid_headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("size", response.data)
        self.assertEqual(response.data["size"][0], "Ensure this value is less than or equal to 10000.")


class TestPartnerInitiatePaymentView(BaseCreateDeveloperApp):
    def setUp(self):
        super().setUp()
        self.url = reverse("v1_partner_initiate_payment")
        self.token = f"{self.app.public_token}:{self.app.private_token}"
        self.valid_headers = {"Authorization": f"Bearer {self.token}"}
        self.linked_account = LinkedAccount.objects.create(
            phone_number=self.phone_number,
            partner_tracking_id=self.app.tracking_id,
            merchant_id=self.app.merchant_id,
            account_tracking_id=self.app.tracking_id,
        )
        self.serializer_data = {
            "amount_in_millimes": 5000,
            "product": "005",
            "phone_number": self.phone_number,
            "tracking_id": self.app.tracking_id,
        }

    @patch("utils.backend_client.FlouciBackendClient.send_money")
    def test_successful_payment(self, mock_send_money):
        mock_send_money.return_value = {
            "success": True,
            "hash": "ezqrstdfyukglihjokk",
            "blockchain_ref": "147582265886625",
            "status_code": 200,
        }

        response = self.client.post(self.url, self.serializer_data, headers=self.valid_headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get("success"))
        self.assertEqual(response.data.get("blockchain_ref"), "147582265886625")

    @patch("utils.backend_client.FlouciBackendClient.send_money")
    def test_wallet_not_active(self, mock_send_money):
        mock_send_money.return_value = {
            "success": False,
            "message": "error: status_code 400 code None",
            "http_status_code": "400",
            "code": None,
            "status_code": 400,
        }

        response = self.client.post(self.url, self.serializer_data, headers=self.valid_headers)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data.get("success"))
        self.assertEqual(response.data.get("http_status_code"), "400")

    def test_invalid_amount(self):
        self.serializer_data["amount_in_millimes"] = 50

        response = self.client.post(self.url, self.serializer_data, headers=self.valid_headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("amount_in_millimes", response.data)
        self.assertEqual(response.data["amount_in_millimes"][0], "Ensure this value is greater than or equal to 1000.")

    @patch("utils.backend_client.FlouciBackendClient.send_money")
    def test_transaction_blocked_due_to_limits(self, mock_send_money):
        mock_send_money.return_value = {
            "success": False,
            "message": "Transaction blocked due to exceeding limits",
            "code": 451,
            "status_code": 451,
        }

        response = self.client.post(self.url, self.serializer_data, headers=self.valid_headers)
        self.assertEqual(response.status_code, 451)


class TestInitiatePosTransaction(BaseCreateDeveloperApp):
    def setUp(self):
        super().setUp()
        self.url = reverse("init_pos_transaction")
        self.token = f"{self.app.public_token}:{self.app.private_token}"
        self.valid_headers = {"Authorization": f"Bearer {self.token}"}
        self.serializer_data = {
            "id_terminal": "99142",
            "serial_number": "21141",
            "payment_method": "card",
            "amount_in_millimes": 5000,
            "gps_transaction_id": "gps123",
            "developer_tracking_id": self.app.tracking_id,
        }

    @patch("utils.backend_client.FlouciBackendClient.generate_pos_transaction")
    def test_pos_transaction_success(self, mock_generate_pos_transaction):
        mock_generate_pos_transaction.return_value = {
            "success": True,
            "terminal_id": "99142",
            "status_code": 200,
        }

        response = self.client.post(self.url, self.serializer_data, headers=self.valid_headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["terminal_id"], "99142")

    def test_missing_required_field(self):
        invalid_data = self.serializer_data.copy()
        del invalid_data["serial_number"]

        response = self.client.post(self.url, invalid_data, headers=self.valid_headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("serial_number", response.data)

    def test_amount_below_minimum(self):
        invalid_data = self.serializer_data.copy()
        invalid_data["amount_in_millimes"] = 50

        response = self.client.post(self.url, invalid_data, headers=self.valid_headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("amount_in_millimes", response.data)
        self.assertEqual(response.data["amount_in_millimes"][0], "Ensure this value is greater than or equal to 1000.")


class TestFetchGPSTransactionStatusView(BaseCreateDeveloperApp):
    def setUp(self):
        super().setUp()
        self.url = reverse("fetch_gps_transaction_status")
        self.token = f"{self.app.public_token}:{self.app.private_token}"
        self.valid_headers = {"Authorization": f"Bearer {self.token}"}

    @patch("utils.backend_client.FlouciBackendClient.fetch_associated_partner_transaction")
    def test_fetch_gps_transaction_status_success(self, mock_fetch_status):
        mock_fetch_status.return_value = {
            "success": True,
            "developer_tracking_id": None,
            "flouci_transaction": "c5836d4f-b426-4724-8f33-218a8c1455f4",
            "payment_status": "PS",
            "status_code": 200,
        }
        self.serializer_data = {
            "flouci_transaction_id": uuid.uuid4(),
        }
        response = self.client.get(self.url, self.serializer_data, headers=self.valid_headers)
        self.assertEqual(response.status_code, 200)

    @patch("utils.backend_client.FlouciBackendClient.fetch_associated_partner_transaction")
    def test_fetch_gps_transaction_with_developer_tracking_id(self, mock_fetch_status):
        mock_fetch_status.return_value = {
            "success": True,
            "developer_tracking_id": "c5886d4f-b426-4724-8f33-218a8c1455f4",
            "flouci_transaction": "c5836d4f-b426-4724-8f33-218a8c1455f4",
            "payment_status": "PS",
            "status_code": 200,
        }
        self.serializer_data = {
            "developer_tracking_id": uuid.uuid4(),
        }
        response = self.client.get(self.url, self.serializer_data, headers=self.valid_headers)
        self.assertEqual(response.status_code, 200)

    @patch("utils.backend_client.FlouciBackendClient.fetch_associated_partner_transaction")
    def test_fetch_gps_transaction_with_both_field(self, mock_fetch_status):
        mock_fetch_status.return_value = {
            "success": True,
            "developer_tracking_id": "c5886d4f-b426-4724-8f33-218a8c1455f4",
            "flouci_transaction": "c5836d4f-b426-4724-8f33-218a8c1455f4",
            "payment_status": "PS",
            "status_code": 200,
        }
        self.serializer_data = {
            "developer_tracking_id": uuid.uuid4(),
            "flouci_transaction": uuid.uuid4(),
        }

        response = self.client.get(self.url, self.serializer_data, headers=self.valid_headers)
        self.assertEqual(response.status_code, 200)

    @patch("utils.backend_client.FlouciBackendClient.fetch_associated_partner_transaction")
    def test_fetch_gps_transaction_not_allowed(self, mock_fetch_status):
        mock_fetch_status.return_value = {"success": False, "status_code": 406, "message": "Not allowed."}
        self.serializer_data = {
            "flouci_transaction_id": uuid.uuid4(),
        }

        response = self.client.get(self.url, self.serializer_data, headers=self.valid_headers)
        self.assertEqual(response.status_code, 406)
        self.assertIn("Not allowed.", response.data["message"])

    @patch("utils.backend_client.FlouciBackendClient.fetch_associated_partner_transaction")
    def test_fetch_gps_transaction_not_found(self, mock_fetch_status):
        mock_fetch_status.return_value = {"success": False, "status_code": 404, "message": "Transaction not found"}
        self.serializer_data = {
            "flouci_transaction_id": uuid.uuid4(),
        }

        response = self.client.get(self.url, self.serializer_data, headers=self.valid_headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn("Transaction not found", response.data["message"])
