import logging
from datetime import timedelta

import requests
from django.utils import timezone

from settings.settings import FLOUCI_BACKEND_API_ADDRESS, FLOUCI_BACKEND_API_KEY

logger = logging.getLogger(__name__)


def handle_exceptions(func):
    """Decorator to handle exceptions and log them."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
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
    CONFIRM_TRANSACTION_URL = f"{FLOUCI_BACKEND_API_ADDRESS}/api/developers/confirm_transaction"
    CANCEL_TRANSACTION_URL = f"{FLOUCI_BACKEND_API_ADDRESS}/api/developers/cancel_transaction"

    @staticmethod
    def _process_response(response, success_code=[200, 201]):
        """Process the HTTP response and standardize error handling."""
        if response.status_code >= 500:
            logger.critical(f"Request failed with status code {response.status_code}. Response: {response.text}")
            return {"success": False, "code": 5, "message": "Service indisponible", "status_code": response.status_code}
        else:
            response_json = response.json()
            if response.status_code in success_code and response_json.get("success"):
                return response_json
            else:
                logger.error(f"Request failed with response: {response.text}")
                return {
                    "success": False,
                    "code": 1,
                    "message": "Error processing request",
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
        is_reservation_payment,
    ):
        data = {
            "test_account": test_account,
            "accept_card": accept_card,
            "amount": amount_in_millimes,
            "amount_in_millimes": amount_in_millimes,
            "merchant_id": merchant_id,
            "app_token": str(app_token),
            "app_secret": str(app_secret),
            "success_link": success_link,
            "fail_link": fail_link,
            "developer_tracking_id": developer_tracking_id,
            "expires_at": (timezone.now() + timedelta(seconds=expires_at)).isoformat(),
            "is_reservation_payment": is_reservation_payment,
        }
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
        )
        return FlouciBackendClient._process_response(response)

    @staticmethod
    @handle_exceptions
    def developer_send_money_status(amount_in_millimes, receiver, sender_id, webhook_url=None):
        data = {
            "amount_in_millimes": amount_in_millimes,
            "receiver": receiver,
            "sender_id": sender_id,
        }
        if webhook_url:
            data["webhook_url"] = webhook_url

        response = requests.post(
            FlouciBackendClient.SEND_MONEY_URL,
            headers=FlouciBackendClient.HEADERS,
            json=data,
        )
        return FlouciBackendClient._process_response(response)

    @staticmethod
    @handle_exceptions
    def developer_check_send_money_status(operation_id, sender_id):
        data = {
            "operation_id": operation_id,
            "sender_id": sender_id,
        }
        response = requests.post(
            FlouciBackendClient.CHECK_SEND_MONEY_STATUS_URL,
            headers=FlouciBackendClient.HEADERS,
            json=data,
        )
        return FlouciBackendClient._process_response(response)

    @staticmethod
    @handle_exceptions
    def confirm_payment(payment_id, amount, merchant_id):
        data = {"payment_id": payment_id, "amount": amount, "merchant_id": merchant_id}
        response = requests.post(
            FlouciBackendClient.CONFIRM_TRANSACTION_URL,
            headers=FlouciBackendClient.HEADERS,
            json=data,
        )
        return FlouciBackendClient._process_response(response)

    @staticmethod
    @handle_exceptions
    def cancel_payment(payment_id, merchant_id):
        data = {"payment_id": payment_id, "merchant_id": merchant_id}
        response = requests.post(
            FlouciBackendClient.CANCEL_TRANSACTION_URL,
            headers=FlouciBackendClient.HEADERS,
            json=data,
        )
        return FlouciBackendClient._process_response(response)
