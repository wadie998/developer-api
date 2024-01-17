from rest_framework import status
from rest_framework.exceptions import APIException


class FlouciCustomException(APIException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = {"error": True, "message": "additional condition failed"}
    default_code = "additional_condition_failed"
