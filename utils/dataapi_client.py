import logging

from settings.settings import DATA_API_ADDRESS, DATA_API_PASSWORD, DATA_API_USERNAME
from utils.token_based_requests_manager import TokenBasedRequests

logger = logging.getLogger(__name__)


# TODO: Better log messages for errors


class DataApiClient:
    request_client = TokenBasedRequests(
        DATA_API_ADDRESS + "/api/authenticate",
        {"password": DATA_API_PASSWORD, "remember_me": 1, "username": DATA_API_USERNAME},
        {"Content-Type": "application/json"},
        accepted_status_codes=[200, 201],
    )
    AUTHENTICATE_URL = DATA_API_ADDRESS + "/api/authenticate"
    ACCEPT_PAYMENT = DATA_API_ADDRESS + "/api/developer/accept"

    @staticmethod
    def accept_payment(self, data):
        data = {
            "code": data["flouci_otp"],
            "appToken": data["app_token"],
            "id": data["payment_id"],
            "amount": convert_millimes_to_drops(data["amount"]),
            "destination": data.get("destination"),
            "developerTrackingId": data.get("developer_tracking_id"),
            "appId": data.get("app_id"),
        }
        response = DataApiClient.request_client.post(DataApiClient.ACCEPT_PAYMENT, data)
        response_data = response.json()
        if response.status_code == 200 and response_data.get("code") == 0:
            transaction_result = response_data.get("result", {})
            payment_response = {
                "status": "SUCCESS",
                "amount": convert_drops_to_millimes(int(transaction_result.get("amount"))),
                "sender": transaction_result.get("account"),
                "transaction_id": transaction_result.get("hash"),
            }
            return {"result": payment_response, "code": 0}
        else:
            return {
                "result": {"status": "FAILED"},
                "code": response_data.get("code", 1),
                "message": response_data.get("message", "Payment failed"),
            }


def convert_millimes_to_drops(millimes):
    return millimes * 100


def convert_drops_to_millimes(drops):
    return drops // 100
