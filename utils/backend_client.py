import logging
from datetime import timedelta

import requests
from django.utils import timezone

from settings.settings import (
    FLOUCI_BACKEND_API_ADDRESS,
    FLOUCI_BACKEND_API_KEY,
    FLOUCI_BACKEND_INTERNAL_API_KEY,
)

logger = logging.getLogger(__name__)

"""
This class is a Backend Client.
Use: result = FlouciBackendClient.get_accepted_users()
"""


class FlouciBackendClient:
    HEADERS = {"Content-Type": "application/json", "Authorization": "Api-Key " + FLOUCI_BACKEND_API_KEY}
    GENERATE_PAYMENT_PAGE_URL = f"{FLOUCI_BACKEND_API_ADDRESS}/api/developers/generate_payment_page"
    CHECK_PAYMENT_URL = f"{FLOUCI_BACKEND_API_ADDRESS}/api/developers/check_payment"
    SEND_MONEY_URL = f"{FLOUCI_BACKEND_API_ADDRESS}/api/developers/send_money"
    CHECK_SEND_MONEY_STATUS_URL = f"{FLOUCI_BACKEND_API_ADDRESS}/api/developers/check_send_money_status"
    FETCH_TRACKING_ID_URL = f"{FLOUCI_BACKEND_API_ADDRESS}/api_internal/fetch_associated_tracking_id"

    @staticmethod
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
    ):
        """
        format date %Y-%m-%d
        """
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
        }
        if webhook_url is not None:
            data["webhook_url"] = webhook_url
        if accept_edinar is not None:
            data["accept_edinar"] = accept_edinar
        if destination is not None:
            data["destination"] = destination
        if currency is not None:
            data["currency"] = currency
        try:
            result = requests.post(
                FlouciBackendClient.GENERATE_PAYMENT_PAGE_URL,
                headers=FlouciBackendClient.HEADERS,
                verify=False,
                json=data,
            )
            return result.json()
        except Exception as e:
            logger.exception(f"An error has occurred generate_payment_page client {app_token} exception: {e}")
            return {"success": False, "error": "Problem while  getting user info", "code": -1, "status_code": 500}

    @staticmethod
    def check_payment(payment_id, wallet, merchant_id):
        params = {"slug": payment_id, "wallet": wallet, "merchant_id": merchant_id}
        try:
            result = requests.get(
                FlouciBackendClient.CHECK_PAYMENT_URL,
                headers=FlouciBackendClient.HEADERS,
                verify=False,
                params=params,
            )
        except Exception as e:
            logger.exception("An error has occurred fetch_wallet_balance %s", e)
            return {"success": False, "code": 6, "message": "Serveur non disponible", "status_code": 500}
        if result.status_code == 200 and result.json()["success"]:
            return result.json()
        else:
            logger.error(
                f"An error has occurred check_payment from wallet {wallet}, status code: {result.status_code}, error details {result.text}",  # noqa: E501
            )
            return {"success": False, "code": 5, "message": "Erreur serveur", "status_code": result.status_code}

    @staticmethod
    def developer_send_money_status(amount_in_millimes, receiver, sender_id, webhook_url=None):
        data = {
            "amount_in_millimes": amount_in_millimes,
            "receiver": receiver,
            "sender_id": sender_id,
        }
        if webhook_url is not None:
            data["webhook_url"] = webhook_url
        try:
            result = requests.post(
                FlouciBackendClient.SEND_MONEY_URL,
                headers=FlouciBackendClient.HEADERS,
                verify=False,
                json=data,
            )
            if result.status_code == 200 and result.json().get("success"):
                return result.json()
            else:
                logger.error(
                    f"An error has occurred developer_send_money_status with amount_in_millimes {amount_in_millimes}, receiver {receiver}, and sender_id {sender_id}, status code: {result.status_code}, error details {result.text}",  # noqa: E501
                )
                return {"success": False, "code": 5, "message": "Erreur serveur", "status_code": result.status_code}
        except Exception as e:
            logger.exception(
                f"An error has occurred developer_send_money_status client with amount_in_millimes {amount_in_millimes}, receiver {receiver}, and sender_id {sender_id} exception: {e}"  # noqa: E501
            )
            return {"success": False, "error": "Problem while sending money", "code": -1, "status_code": 500}

    @staticmethod
    def developer_check_send_money_status(operation_id, sender_id):
        data = {
            "operation_id": operation_id,
            "sender_id": sender_id,
        }
        try:
            result = requests.post(
                FlouciBackendClient.CHECK_SEND_MONEY_STATUS_URL,
                headers=FlouciBackendClient.HEADERS,
                verify=False,
                json=data,
            )
            if result.status_code == 200 and result.json().get("success"):
                return result.json()
            else:
                logger.error(
                    f"An error has occurred developer_send_money with operation_id {operation_id} and sender_id {sender_id}, status code: {result.status_code}, error details {result.text}",  # noqa: E501
                )
                return {"success": False, "code": 5, "message": "Erreur serveur", "status_code": result.status_code}
        except Exception as e:
            logger.exception(
                f"An error has occurred developer_send_money client with operation_id {operation_id} and sender_id {sender_id} exception: {e}"  # noqa: E501
            )
            return {"success": False, "error": "Problem while sending money", "code": -1, "status_code": 500}

    @staticmethod
    def fetch_tracking_id(wallet):
        params = {"wallet": wallet}
        header = FlouciBackendClient.HEADERS
        header["Authorization"] = "Api-Key " + FLOUCI_BACKEND_INTERNAL_API_KEY
        try:
            result = requests.get(
                FlouciBackendClient.FETCH_TRACKING_ID_URL,
                headers=FlouciBackendClient.HEADERS,
                verify=False,
                params=params,
            )
            if result.status_code == 200 and result.json().get("success"):
                return result.json()
            else:
                logger.error(
                    f"An error has occurred fetch_tracking_id from wallet {wallet}, status code: {result.status_code}, error details {result.text}",  # noqa: E501
                )
                return {"success": False, "status_code": result.status_code}
        except Exception as e:
            logger.exception("An error has occurred fetch_tracking_id %s", e)
            return {"success": False, "code": 6, "message": "Serveur non disponible", "status_code": 500}

        pass
