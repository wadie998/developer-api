from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from api.models import FlouciApp
from api.permissions import HasValidAppCredentials
from api.serializers import (
    AddPosTransactionSerializer,
    CheckSendMoneyStatusSerializer,
    GeneratePaymentSerializer,
    SecureAcceptPaymentSerializer,
    SendMoneySerializer,
    VerifyPaymentSerializer,
)
from settings.settings import DJANGO_SERVICE_VERSION
from utils.backend_client import FlouciBackendClient
from utils.dataapi_client import DataApiClient
from utils.decorators import IsValidGenericApi


@extend_schema(
    tags=["Accept-Payments"],
    summary="Generate Payment Page",
    description=(
        "This endpoint generates a payment page for the user. "
        "The user can specify various parameters such as the amount, currency, and payment methods accepted. "
        "Upon success, a URL to the payment page is returned along with a payment ID."
    ),
    request=GeneratePaymentSerializer,
    responses={
        200: {
            "description": "Payment page generated successfully",
            "examples": {
                "application/json": {
                    "result": {
                        "link": "https://payment.page.url",
                        "payment_id": "123456789",
                        "developer_tracking_id": "dev_track_id",
                        "success": True,
                    },
                    "name": "developers",
                    "code": 0,
                    "version": "5.0.0",
                }
            },
        },
        400: {
            "description": "Invalid request data",
            "examples": {
                "application/json": {
                    "result": {"success": False, "error": "Invalid data", "details": "Detailed error message"},
                    "name": "developers",
                    "code": 1,
                    "version": "5.0.0",
                }
            },
        },
    },
)
@IsValidGenericApi()
class GeneratePaymentView(GenericAPIView):
    serializer_class = GeneratePaymentSerializer
    permission_classes = (HasValidAppCredentials,)

    def post(self, request, serializer):
        app_token = serializer.validated_data.get("app_token")
        app_secret = serializer.validated_data.get("app_secret")
        amount_in_millimes = serializer.validated_data.get("amount_in_millimes")
        accept_card = serializer.validated_data.get("accept_card")
        accept_edinar = serializer.validated_data.get("accept_edinar")
        currency = serializer.validated_data.get("currency")
        session_timeout_secs = serializer.validated_data.get("session_timeout_secs")
        session_timeout = serializer.validated_data.get("session_timeout")
        success_link = serializer.validated_data.get("success_link")
        fail_link = serializer.validated_data.get("fail_link")
        webhook = serializer.validated_data.get("webhook")
        developer_tracking_id = serializer.validated_data.get("developer_tracking_id")
        destination = serializer.validated_data.get("destination")
        test_account = serializer.validated_data.get("test")
        merchant_id = serializer.validated_data.get("merchant_id")

        response = FlouciBackendClient.generate_payment_page(
            test_account=test_account,
            accept_card=accept_card,
            accept_edinar=accept_edinar,
            amount_in_millimes=amount_in_millimes,
            currency=currency,
            merchant_id=merchant_id,
            app_token=app_token,
            app_secret=app_secret,
            success_link=success_link,
            fail_link=fail_link,
            developer_tracking_id=developer_tracking_id,
            expires_at=session_timeout_secs or session_timeout,
            webhook_url=webhook,
            destination=destination,
        )
        if response.get("success"):
            data = {
                "result": {
                    "link": response.get("url"),
                    "payment_id": response.get("payment_id"),
                    "developer_tracking_id": developer_tracking_id,
                    "success": True,
                },
                "name": "developers",
                "code": 0,
                "version": DJANGO_SERVICE_VERSION,
            }
        else:
            data = {
                "result": {
                    "success": False,
                    "error": response.get("result"),
                    "details": response.get("non_field_errors"),
                },
                "name": "developers",
                "code": 1,
                "version": DJANGO_SERVICE_VERSION,
            }
        return Response(data=data, status=response.get("status_code"))


@extend_schema(
    tags=["Accept-Payments"],
    summary="Verify Payment",
    description=(
        "This endpoint verifies the status of a payment. "
        "The user can provide the payment ID to check the current status of the payment."
    ),
    request=VerifyPaymentSerializer,
    responses={
        200: {
            "description": "Payment verified successfully",
            "examples": {
                "application/json": {
                    "result": {
                        "payment_status": "completed",
                        "payment_id": "123456789",
                        "success": True,
                    },
                    "name": "developers",
                    "code": 0,
                    "version": "5.0.0",
                }
            },
        },
        400: {
            "description": "Invalid request data",
            "examples": {
                "application/json": {
                    "result": {"success": False, "error": "Invalid data", "details": "Detailed error message"},
                    "name": "developers",
                    "code": 1,
                    "version": "5.0.0",
                }
            },
        },
    },
)
@IsValidGenericApi(post=False, get=True)
class VerifyPaymentView(GenericAPIView):
    serializer_class = VerifyPaymentSerializer
    permission_classes = (HasValidAppCredentials,)

    def get(self, request, serializer):
        payment_id = serializer.validated_data["payment_id"]
        application = request.application
        # TODO change in backend and depricate the wallet field
        response = FlouciBackendClient.check_payment(
            payment_id=payment_id, wallet=application.wallet, merchant_id=application.merchant_id
        )
        if response.get("success"):
            data = {
                "result": {
                    "payment_status": response.get("status"),
                    "payment_id": payment_id,
                    "success": True,
                },
                "name": "developers",
                "code": 0,
                "version": DJANGO_SERVICE_VERSION,
            }
        else:
            data = {
                "result": {
                    "success": False,
                    "error": response.get("result"),
                    "details": response.get("non_field_errors"),
                },
                "name": "developers",
                "code": 1,
                "version": DJANGO_SERVICE_VERSION,
            }
        return Response(data=data, status=response.get("status_code"))


@extend_schema(
    tags=["Orchestration-Payments"],
    summary="Send Money",
    description=(
        "This endpoint allows the user to send money to a specified destination. "
        "The user can specify the amount, destination, and webhook URL for notifications."
    ),
    request=SendMoneySerializer,
    responses={
        200: {
            "description": "Money sent successfully",
            "examples": {
                "application/json": {
                    "result": {
                        "transaction_status": "completed",
                        "transaction_id": "987654321",
                        "success": True,
                    },
                    "name": "developers",
                    "code": 0,
                    "version": "5.0.0",
                }
            },
        },
        400: {
            "description": "Invalid request data",
            "examples": {
                "application/json": {
                    "result": {"success": False, "error": "Invalid data", "details": "Detailed error message"},
                    "name": "developers",
                    "code": 1,
                    "version": "5.0.0",
                }
            },
        },
    },
)
@IsValidGenericApi(post=True, get=False)
class SendMoneyView(GenericAPIView):
    serializer_class = SendMoneySerializer
    permission_classes = (HasValidAppCredentials,)

    def post(self, request, serializer):
        validated_data = serializer.validated_data

        response = FlouciBackendClient.developer_send_money_status(
            amount_in_millimes=validated_data.get("amount_in_millimes"),
            destination=validated_data.get("destination"),
            webhook=validated_data.get("webhook"),
            wallet=request.application.wallet,
        )
        if response["success"]:
            data = {
                "result": {
                    "transaction_status": response.get("status"),
                    "transaction_id": response.get("transaction_id"),
                    "success": True,
                },
                "name": "developers",
                "code": 0,
                "version": DJANGO_SERVICE_VERSION,
            }
        else:
            data = {
                "result": {
                    "success": False,
                    "error": response.get("result"),
                    "details": response.get("non_field_errors"),
                },
                "name": "developers",
                "code": 1,
                "version": DJANGO_SERVICE_VERSION,
            }
        return Response(data=data, status=response.get("status_code"))


@extend_schema(
    tags=["Orchestration-Payments"],
    summary="Check Send Money Status",
    description=(
        "This endpoint checks the status of a money sending operation. "
        "The user can provide the operation ID and sender ID to get the current status."
    ),
    request=CheckSendMoneyStatusSerializer,
    responses={
        200: {
            "description": "Send money status checked successfully",
            "examples": {
                "application/json": {
                    "result": {
                        "transaction_status": "completed",
                        "transaction_id": "987654321",
                        "success": True,
                    },
                    "name": "check_send_money_status",
                    "code": 0,
                    "version": "5.0.0",
                }
            },
        },
        400: {
            "description": "Invalid request data",
            "examples": {
                "application/json": {
                    "result": {"success": False, "error": "Invalid data", "details": "Detailed error message"},
                    "name": "check_send_money_status",
                    "code": 1,
                    "version": "5.0.0",
                }
            },
        },
    },
)
@IsValidGenericApi(post=False, get=True)
class CheckSendMoneyStatusView(GenericAPIView):
    serializer_class = CheckSendMoneyStatusSerializer
    permission_classes = (HasValidAppCredentials,)

    def get(self, request, serializer):
        sender_id = request.application.merchant_id
        operation_id = serializer.validated_data["operation_id"]
        response = FlouciBackendClient.developer_check_send_money_status(operation_id=operation_id, sender_id=sender_id)

        if response["success"]:
            data = {
                "result": {
                    "transaction_status": response.get("status"),
                    "transaction_id": response.get("transaction_id"),
                    "success": True,
                },
                "name": "check_send_money_status",
                "code": 0,
                "version": DJANGO_SERVICE_VERSION,
            }
        else:
            data = {
                "result": {
                    "success": False,
                    "error": response.get("result"),
                    "details": response.get("non_field_errors"),
                },
                "name": "check_send_money_status",
                "code": 1,
                "version": DJANGO_SERVICE_VERSION,
            }
        return Response(data=data, status=response.get("status_code"))


@IsValidGenericApi()
class AcceptPayment(GenericAPIView):
    permission_classes = (HasValidAppCredentials,)
    serializer_class = SecureAcceptPaymentSerializer

    def post(self, request, serializer):
        accept_payment_data = serializer.validated_data
        app = FlouciApp.objects.get(private_token=serializer.validated_data["app_secret"])
        if app.test:
            flouci_otp = serializer.validated_data["flouci_otp"]
            if flouci_otp == "F-111111":
                return Response({"result": {"status": "SUCCESS"}, "code": 0}, status=status.HTTP_200_OK)
            if flouci_otp == "F-000000":
                return Response({"result": {"status": "FAILED"}, "code": 0}, status=status.HTTP_200_OK)
        accept_payment_data["app_id"] = app.app_id
        accept_payment_data["destination"] = app.wallet

        response = DataApiClient.accept_payment(accept_payment_data)
        return Response(response, status=status.HTTP_200_OK)


@IsValidGenericApi()
class AddPosTransaction(GenericAPIView):
    permission_classes = (HasValidAppCredentials,)
    serializer_class = AddPosTransactionSerializer

    def post(self, request, serializer):
        try:
            app = FlouciApp.objects.get(private_token=serializer.validated_data["app_secret"])
        except FlouciApp.DoesNotExist:
            return Response({"result": False, "code": 0}, status=status.HTTP_404_NOT_FOUND)
        merchant_id = app.merchant_id
        response = FlouciBackendClient.generate_pos_transaction(
            merchant_id=merchant_id,
            webhook_url=serializer.validated_data["webhook_url"],
            id_terminal=serializer.validated_data["id_terminal"],
            serial_number=serializer.validated_data["serial_number"],
            service_code=serializer.validated_data["service_code"],
            amount_in_millimes=serializer.validated_data["amount_in_millimes"],
            payment_method=serializer.validated_data["payment_method"],
        )
        return Response(response, status=response.get("status_code", 200))
