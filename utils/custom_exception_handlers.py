import logging

from requests import ConnectionError, Timeout
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

from .custom_exceptions import AdditionalConditionFailed

logger = logging.getLogger(__name__)


def drf_custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, ValidationError):
        raise AdditionalConditionFailed()

    if isinstance(exc, ConnectionError) or isinstance(exc, Timeout):
        err_data = {"success": False, "message": "External server connection issue"}
        logging.error(f"Connection issue  detail: {exc}")
        return Response(data=err_data, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    return response
