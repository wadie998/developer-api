from rest_framework import status
from rest_framework.exceptions import APIException


class AdditionalConditionFailed(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {"error": True, "message": "additional condition failed"}
    default_code = "additional_condition_failed"
