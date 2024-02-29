import logging

import requests

from settings.settings import BACKEND_API_ADDRESS, BACKEND_API_KEY

logger = logging.getLogger(__name__)


class BackendApi:
    HEADERS = {"Content-Type": "application/json", "api-key": BACKEND_API_KEY}

    ACTIVATE_CARD = BACKEND_API_ADDRESS + "/api_internal/activate_card"

    @staticmethod
    def activate_card(code, request_id):
        headers = {"Authorization": f"Api-Key {BACKEND_API_KEY}", "Content-Type": "application/json"}
        data = {"code": code, "request_id": str(request_id)}
        try:
            result = requests.post(BackendApi.ACTIVATE_CARD, headers=headers, json=data)
        except Exception as e:
            logger.error(
                "An error has occurred in activate card details: %s",
                e,
            )
            return False
        if result.status_code == 200:
            return True
        else:
            logger.error(
                "An error has occurred in  activate card detils requests status code %s: response %s",
                result.status_code,
                result.text,
            )
            return False
