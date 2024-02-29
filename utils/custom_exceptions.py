from django.http import JsonResponse
from rest_framework import status
from rest_framework.exceptions import APIException


class FlouciCustomException(APIException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = {"error": True, "message": "additional condition failed"}
    default_code = "additional_condition_failed"


class CustomJhipsterxception(Exception):
    def __init__(self, title, detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, path=None, message=None):
        self.title = title
        self.detail = detail
        self.status_code = status_code
        self.path = path
        self.message = message

    def to_response(self):
        response_data = {
            "type": "https://www.jhipster.tech/problem/problem-with-message",
            "title": self.title,
            "status": self.status_code,
            "detail": self.detail,
        }
        if self.path:
            response_data["path"] = self.path
        if self.message:
            response_data["message"] = self.message

        return JsonResponse(response_data, status=self.status_code)
