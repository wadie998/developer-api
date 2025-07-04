import logging
from datetime import timedelta

import requests
from django.urls import reverse
from django.utils import timezone

from api.enum import TransactionsTypes
from settings.settings import (
    DEVELOPER_API_INTERNAL_ADDRESS,
    FLOUCI_BACKEND_API_ADDRESS,
    FLOUCI_BACKEND_API_KEY,
    FLOUCI_BACKEND_INTERNAL_API_KEY,
    SHORT_EXTERNAL_REQUESTS_TIMEOUT,
)
from utils.dataapi_client import convert_millimes_to_dinars

logger = logging.getLogger(__name__)


def handle_exceptions(func):
    """Decorator to handle exceptions and log them."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.Timeout:
            logger.error(f"Timeout occurred in {func.__name__}")
            return {"success": False, "error": "Request timed out", "code": -2, "status_code": 408}
        except Exception as e:
            logger.critical(f"Exception in {func.__name__}: {e}")
            return {"success": False, "error": "Problem processing request", "code": -1, "status_code": 500}

    return wrapper


class FlouciBackendClient:
    HEADERS = {"Content-Type": "application/json", "Authorization": "Api-Key " + FLOUCI_BACKEND_API_KEY}
    GENERATE_PAYMENT_PAGE_URL = f"{FLOUCI_BACKEND_API_ADDRESS}/api/developers/generate_payment_page"
    CHECK_PAYMENT_URL = f"{FLOUCI_BACKEND_API_ADDRESS}/api/developers/check_payment"
    SEND_MONEY_URL = f"{FLOUCI_BACKEND_API_ADDRESS}/api/developers/send_money"
    CHECK_SEND_MONEY_STATUS_URL = f"{FLOUCI_BACKEND_API_ADDRESS}/api/developers/check_send_money_status"
    FETCH_TRACKING_ID_URL = f"{FLOUCI_BACKEND_API_ADDRESS}/api_internal/fetch_associated_tracking_id"
    GENERATE_EXTERNAL_POS_TRANSACTION = f"{FLOUCI_BACKEND_API_ADDRESS}/api/developers/generate_external_pos_transaction"
    FETCH_PARTNER_TRANSACTION_STATUS = f"{FLOUCI_BACKEND_API_ADDRESS}/api/developers/fetch_patner_transaction_status"

    # PARTNER APIs
    IS_FLOUCI = f"{FLOUCI_BACKEND_API_ADDRESS}/api/developers/partners/is_flouci"
    INITIATE_LINK_ACCOUNT = f"{FLOUCI_BACKEND_API_ADDRESS}/api/developers/partners/initiate_link_flouci_account"
    CONFIRM_LINK_ACCOUNT = f"{FLOUCI_BACKEND_API_ADDRESS}/api/developers/partners/confirm_link_flouci_account"
    PARTNER_AUTHENTICATE = f"{FLOUCI_BACKEND_API_ADDRESS}/api/developers/partners/authenticate_user"
    GET_BALANCE = f"{FLOUCI_BACKEND_API_ADDRESS}/api/developers/partners/get_balance"
    SEND_MONEY = f"{FLOUCI_BACKEND_API_ADDRESS}/api/developers/partners/send_money"
    CONFIRM_PAYMENT_AUTHORIZATION_URL = f"{FLOUCI_BACKEND_API_ADDRESS}/api/developers/confirm_pre_authorized_payment"
    CANCEL_PAYMENT_AUTHORIZATION_URL = f"{FLOUCI_BACKEND_API_ADDRESS}/api/developers/cancel_pre_authorized_payment"
    REFUND_POS_PAYMENT_URL = f"{FLOUCI_BACKEND_API_ADDRESS}/api/developers/refund_pos_transaction"

    @staticmethod
    def _process_response(response, success_code=[200, 201, 204]):
        """Process the HTTP response and standardize error handling."""
        if response.status_code >= 500:
            logger.critical(f"Request failed with status code {response.status_code}. Response: {response.text}")
            return {"success": False, "code": 5, "message": "Service indisponible", "status_code": response.status_code}
        else:
            response_json = response.json()
            if response.status_code in success_code:
                return {"success": True, **response_json, "status_code": response.status_code}
            elif response.status_code >= 400:
                return {"success": False, **response_json, "code": 1, "status_code": response.status_code}
            else:
                return {
                    "success": False,
                    "code": 1,
                    "message": f"{response.text}",
                    "status_code": response.status_code,
                }

    @staticmethod
    @handle_exceptions
    def generate_payment_page(
        test_account,
        accept_card,
        accept_edinar,
        amount_in_millimes,
        currency,
        merchant_id,
        app_token,
        app_secret,
        success_link,
        fail_link,
        developer_tracking_id,
        expires_at,
        webhook_url,
        destination,
        pre_authorization,
    ):
        data = {
            "test_account": test_account,
            "accept_card": accept_card,
            "amount": str(convert_millimes_to_dinars(amount_in_millimes)),
            "amount_in_millimes": amount_in_millimes,
            "merchant_id": merchant_id,
            "app_token": str(app_token),
            "app_secret": str(app_secret),
            "success_link": success_link,
            "fail_link": fail_link,
            "developer_tracking_id": developer_tracking_id,
            "pre_authorization": pre_authorization,
        }
        if expires_at:
            data["expires_at"] = (timezone.now() + timedelta(seconds=expires_at)).isoformat()
        if webhook_url:
            data["webhook_url"] = webhook_url
        if accept_edinar:
            data["accept_edinar"] = accept_edinar
        if destination:
            data["destination"] = destination
        if currency:
            data["currency"] = currency

        response = requests.post(
            FlouciBackendClient.GENERATE_PAYMENT_PAGE_URL,
            headers=FlouciBackendClient.HEADERS,
            json=data,
            timeout=SHORT_EXTERNAL_REQUESTS_TIMEOUT,
        )
        return FlouciBackendClient._process_response(response)

    @staticmethod
    @handle_exceptions
    def check_payment(payment_id, wallet, merchant_id):
        params = {"slug": payment_id, "wallet": wallet, "merchant_id": merchant_id}
        response = requests.get(
            FlouciBackendClient.CHECK_PAYMENT_URL,
            headers=FlouciBackendClient.HEADERS,
            params=params,
            timeout=SHORT_EXTERNAL_REQUESTS_TIMEOUT,
        )
        return FlouciBackendClient._process_response(response)

    @staticmethod
    @handle_exceptions
    def developer_send_money_status(amount_in_millimes, receiver, sender_id, webhook=None):
        data = {
            "amount_in_millimes": amount_in_millimes,
            "receiver": receiver,
            "sender_id": sender_id,
        }
        if webhook:
            data["webhook_url"] = webhook

        response = requests.post(
            FlouciBackendClient.SEND_MONEY_URL,
            headers=FlouciBackendClient.HEADERS,
            json=data,
            timeout=SHORT_EXTERNAL_REQUESTS_TIMEOUT,
        )
        return FlouciBackendClient._process_response(response)

    @staticmethod
    @handle_exceptions
    def developer_check_send_money_status(operation_id, sender_id):
        params = {
            "operation_id": operation_id,
            "sender_id": sender_id,
        }
        response = requests.get(
            FlouciBackendClient.CHECK_SEND_MONEY_STATUS_URL,
            headers=FlouciBackendClient.HEADERS,
            params=params,
            timeout=SHORT_EXTERNAL_REQUESTS_TIMEOUT,
        )
        return FlouciBackendClient._process_response(response)

    @staticmethod
    @handle_exceptions
    def generate_pos_transaction(
        merchant_id,
        webhook,
        id_terminal,
        serial_number,
        service_code,
        amount_in_millimes,
        payment_method,
        developer_tracking_id,
        parent_payment_id=None,
    ):
        data = {
            "merchant_id": merchant_id,
            "idTerminal": id_terminal,
            "serialNumber": serial_number,
            "serviceCode": service_code,
            "amount_in_millimes": amount_in_millimes,
            "payment_method": payment_method,
            "developer_tracking_id": developer_tracking_id,
        }
        if parent_payment_id:
            data["parent_payment_id"] = parent_payment_id
        if webhook:
            data["webhook"] = webhook
        response = requests.post(
            FlouciBackendClient.GENERATE_EXTERNAL_POS_TRANSACTION,
            headers=FlouciBackendClient.HEADERS,
            json=data,
            timeout=SHORT_EXTERNAL_REQUESTS_TIMEOUT,
        )
        return FlouciBackendClient._process_response(response)

    @staticmethod
    @handle_exceptions
    def fetch_associated_partner_transaction(
        merchant_id, *, developer_tracking_id: str = None, flouci_transaction_id: str = None
    ):
        params = {"merchant_id": merchant_id}
        if flouci_transaction_id:
            params["transaction_id"] = flouci_transaction_id
        else:
            params["developer_tracking_id"] = developer_tracking_id
        response = requests.get(
            FlouciBackendClient.FETCH_PARTNER_TRANSACTION_STATUS,
            headers=FlouciBackendClient.HEADERS,
            params=params,
            timeout=SHORT_EXTERNAL_REQUESTS_TIMEOUT,
        )
        return FlouciBackendClient._process_response(response)

    @staticmethod
    @handle_exceptions
    def refund_pos_transaction(id_terminal, serial_number, reason, merchant_id, developer_tracking_id: str = None, flouci_transaction_id: str = None):
        data = {
            "id_terminal": id_terminal,
            "serial_number": serial_number,
            "reason": reason,
            "merchant_id": merchant_id,
            "developer_tracking_id": developer_tracking_id,
            "flouci_transaction_id": flouci_transaction_id,
        }
        response = requests.post(
            FlouciBackendClient.REFUND_POS_PAYMENT_URL,
            headers=FlouciBackendClient.HEADERS,
            json=data,
            timeout=SHORT_EXTERNAL_REQUESTS_TIMEOUT,
        )
        return FlouciBackendClient._process_response(response)


    @staticmethod
    @handle_exceptions
    def initiate_link_account(phone_number, merchant_id):
        data = {
            "phone_number": phone_number,
            "merchant_id": merchant_id,
        }
        response = requests.post(
            FlouciBackendClient.INITIATE_LINK_ACCOUNT,
            headers=FlouciBackendClient.HEADERS,
            json=data,
            timeout=SHORT_EXTERNAL_REQUESTS_TIMEOUT,
        )
        return FlouciBackendClient._process_response(response)

    @staticmethod
    @handle_exceptions
    def is_flouci(phone_number, merchant_id):
        data = {
            "phone_number": phone_number,
            "merchant_id": merchant_id,
        }
        response = requests.post(
            FlouciBackendClient.IS_FLOUCI,
            headers=FlouciBackendClient.HEADERS,
            json=data,
            timeout=SHORT_EXTERNAL_REQUESTS_TIMEOUT,
        )
        return FlouciBackendClient._process_response(response)

    @staticmethod
    @handle_exceptions
    def confirm_link_account(phone_number, session_id, otp, merchant_id):
        data = {
            "phone_number": phone_number,
            "session_id": str(session_id),
            "otp": otp,
            "merchant_id": merchant_id,
        }
        response = requests.post(
            FlouciBackendClient.CONFIRM_LINK_ACCOUNT,
            headers=FlouciBackendClient.HEADERS,
            json=data,
            timeout=SHORT_EXTERNAL_REQUESTS_TIMEOUT,
        )
        return FlouciBackendClient._process_response(response)

    @staticmethod
    @handle_exceptions
    def generate_authentication_token(phone_number, partner_tracking_id, account_tracking_id, merchant_id):
        data = {
            "phone_number": phone_number,
            "account_tracking_id": str(account_tracking_id),
            "partner_tracking_id": str(partner_tracking_id),
            "merchant_id": merchant_id,
        }
        response = requests.post(
            FlouciBackendClient.PARTNER_AUTHENTICATE,
            headers=FlouciBackendClient.HEADERS,
            json=data,
            timeout=SHORT_EXTERNAL_REQUESTS_TIMEOUT,
        )
        return FlouciBackendClient._process_response(response)

    @staticmethod
    @handle_exceptions
    def get_user_balance(tracking_id):
        data = {
            "account_tracking_id": str(tracking_id),
        }
        response = requests.post(
            FlouciBackendClient.GET_BALANCE,
            headers=FlouciBackendClient.HEADERS,
            json=data,
            timeout=SHORT_EXTERNAL_REQUESTS_TIMEOUT,
        )
        return FlouciBackendClient._process_response(response)

    @staticmethod
    @handle_exceptions
    def send_money(operation, merchant_id=None, receiver=None):
        # TODO add receiver can be merchant

        data = {
            "operation_id": str(operation.operation_id),
            "transaction_type": TransactionsTypes.P2P.value if operation.receiver else TransactionsTypes.MERCHANT.value,
            "account_tracking_id": str(operation.sender.account_tracking_id),
            "amount_in_millimes": operation.amount_in_millimes,
            "webhook": DEVELOPER_API_INTERNAL_ADDRESS + reverse("internal_send_money_catcher"),
        }
        logger.info(f"Data send_money {data}")
        if merchant_id:
            data["merchant_id"] = merchant_id
        if receiver:
            data["receiver"] = receiver
        response = requests.post(
            FlouciBackendClient.SEND_MONEY,
            headers=FlouciBackendClient.HEADERS,
            json=data,
            timeout=SHORT_EXTERNAL_REQUESTS_TIMEOUT,
        )
        return FlouciBackendClient._process_response(response)

    @staticmethod
    @handle_exceptions
    def confirm_payment(payment_id, amount, merchant_id):
        data = {"payment_id": payment_id, "amount": amount, "merchant_id": merchant_id}
        response = requests.post(
            FlouciBackendClient.CONFIRM_PAYMENT_AUTHORIZATION_URL,
            headers=FlouciBackendClient.HEADERS,
            json=data,
            timeout=SHORT_EXTERNAL_REQUESTS_TIMEOUT,
        )
        return FlouciBackendClient._process_response(response)

    @staticmethod
    @handle_exceptions
    def cancel_payment(payment_id, merchant_id):
        data = {"payment_id": payment_id, "merchant_id": merchant_id}
        response = requests.post(
            FlouciBackendClient.CANCEL_PAYMENT_AUTHORIZATION_URL,
            headers=FlouciBackendClient.HEADERS,
            json=data,
            timeout=SHORT_EXTERNAL_REQUESTS_TIMEOUT,
        )
        return FlouciBackendClient._process_response(response)

    def fetch_associated_tracking_id(wallet):
        params = {
            "wallet": wallet,
        }
        headers = {"Content-Type": "application/json", "Authorization": "Api-Key " + FLOUCI_BACKEND_INTERNAL_API_KEY}
        response = requests.get(
            FlouciBackendClient.FETCH_TRACKING_ID_URL,
            headers=headers,
            params=params,
            timeout=SHORT_EXTERNAL_REQUESTS_TIMEOUT,
        )
        return FlouciBackendClient._process_response(response)
