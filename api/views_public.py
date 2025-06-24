from http import HTTPStatus

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from api.models import FlouciApp
from api.permissions import HasValidAppCredentials, HasValidAppCredentialsV2
from api.serializers import (
    AcceptPaymentSerializer,
    BaseCheckSendMoneyStatusSerializer,
    BaseSendMoneySerializer,
    CancelSMTPreAuthorizationSerializer,
    CheckSendMoneyStatusSerializer,
    ConfirmSMTPreAuthorizationSerializer,
    GeneratePaymentSerializer,
    OldGeneratePaymentSerializer,
    SecureAcceptPaymentSerializer,
    SendMoneySerializer,
    VerifyPaymentSerializer,
)
from settings.settings import DJANGO_SERVICE_VERSION
from utils.backend_client import FlouciBackendClient
from utils.dataapi_client import DataApiClient
from utils.decorators import IsValidGenericApi


@IsValidGenericApi()
class BaseGeneratePaymentView(GenericAPIView):
    depricated = True

    def post(self, request, serializer):
        """Handles both V1 (deprecated) and V2 dynamically."""
        if self.depricated:
            app_token = serializer.validated_data.get("app_token")
            app_secret = serializer.validated_data.get("app_secret")
            version = "v1 (deprecated)"
        else:
            application: FlouciApp = request.application
            app_token = application.public_token
            app_secret = application.private_token
            version = "v2"

        application: FlouciApp = request.application
        app_token = application.public_token
        app_secret = application.private_token
        test_account = application.test
        merchant_id = application.merchant_id
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
        pre_authorization = serializer.validated_data["pre_authorization"]

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
            pre_authorization=pre_authorization,
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
                "version": version,
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
                "version": version,
            }
        return Response(data=data, status=response.get("status_code"))


@extend_schema_view(
    post=extend_schema(
        tags=["Accept-Payments"],
        summary="Generate Payment Page (V1)",
        description=(
            "This endpoint generates a payment page for the user (Version 1). "
            "It requires `app_token` and `app_secret` in the request body."
        ),
        request=OldGeneratePaymentSerializer,
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
        deprecated=True,  # Marking it as deprecated
    )
)
class OldGeneratePaymentView(BaseGeneratePaymentView):
    serializer_class = OldGeneratePaymentSerializer
    permission_classes = (HasValidAppCredentials,)


@extend_schema(exclude=True)
class OldGeneratePaymentWordpressView(OldGeneratePaymentView):
    pass


@extend_schema_view(
    post=extend_schema(
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
)
class GeneratePaymentView(BaseGeneratePaymentView):
    serializer_class = GeneratePaymentSerializer
    permission_classes = (HasValidAppCredentialsV2,)


@extend_schema(exclude=True)
class GeneratePaymentWordpressView(GeneratePaymentView):
    pass


@IsValidGenericApi(post=False, get=True)
class BaseVerifyPaymentView(GenericAPIView):
    serializer_class = VerifyPaymentSerializer

    def get(self, request, serializer):
        payment_id = serializer.validated_data["payment_id"]
        application = request.application
        # TODO change in backend and depricate the wallet field
        response = FlouciBackendClient.check_payment(
            payment_id=payment_id, wallet=application.wallet, merchant_id=application.merchant_id
        )
        if response.get("success"):
            data = {
                **response,
                "name": "developers",
                "code": 0,
                "version": DJANGO_SERVICE_VERSION,
            }
        else:
            data = {
                **response,
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
    deprecated=True,
)
class OldVerifyPaymentView(BaseVerifyPaymentView):
    permission_classes = (HasValidAppCredentials,)


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
class VerifyPaymentView(BaseVerifyPaymentView):
    permission_classes = (HasValidAppCredentialsV2,)


@IsValidGenericApi(post=True, get=False)
class BaseSendMoneyView(GenericAPIView):

    def post(self, request, serializer):
        application: FlouciApp = request.application
        if application.test:
            return Response(
                data={
                    "result": {
                        "success": False,
                        "error": "Can't send money through test App",
                        "code": 406,
                    },
                    "name": "developers",
                    "code": 1,
                    "version": DJANGO_SERVICE_VERSION,
                },
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )
        validated_data = serializer.validated_data

        response = FlouciBackendClient.developer_send_money_status(
            amount_in_millimes=validated_data.get("amount_in_millimes"),
            receiver=validated_data.get("destination"),
            webhook=validated_data.get("webhook"),
            sender_id=application.merchant_id,
        )
        status_code = response.get("status_code")
        if response["success"]:
            data = {
                "result": {
                    "code": 0,
                    "success": True,
                    "message": response.get("message"),
                    "payment_id": response.get("payment_id"),
                    "status": f"{HTTPStatus(status_code).phrase}",
                },
                "name": "developers",
                "code": 0,
                "version": DJANGO_SERVICE_VERSION,
            }
        else:
            data = {
                "result": {
                    "success": False,
                    "error": response.get("message"),
                    "code": response.get("code"),
                },
                "name": "developers",
                "code": 1,
                "version": DJANGO_SERVICE_VERSION,
            }
        return Response(data=data, status=status_code)


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
    deprecated=True,  # Marking it as deprecated
)
class OldSendMoneyView(BaseSendMoneyView):
    serializer_class = SendMoneySerializer
    permission_classes = (HasValidAppCredentials,)


@extend_schema(
    tags=["Orchestration-Payments"],
    summary="Send Money",
    description=(
        "This endpoint allows the user to send money to a specified destination. "
        "The user can specify the amount, destination, and webhook URL for notifications."
    ),
    request=BaseSendMoneySerializer,
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
class SendMoneyView(BaseSendMoneyView):
    serializer_class = BaseSendMoneySerializer
    permission_classes = (HasValidAppCredentialsV2,)


@IsValidGenericApi(post=False, get=True)
class BaseCheckSendMoneyStatusView(GenericAPIView):
    def get(self, request, serializer):
        sender_id = request.application.merchant_id
        operation_id = serializer.validated_data["operation_id"]
        response = FlouciBackendClient.developer_check_send_money_status(operation_id=operation_id, sender_id=sender_id)
        status_code = response["status_code"]

        if response["success"]:
            data = {
                "success": True,
                **response,
                "httpStatus": f"{HTTPStatus(status_code).phrase}",
                "code": 0,
                "version": DJANGO_SERVICE_VERSION,
            }
        else:
            data = {
                "success": False,
                **response,
                "httpStatus": f"{HTTPStatus(status_code).phrase}",
                "code": 1,
                "version": DJANGO_SERVICE_VERSION,
            }
        return Response(data=data, status=status_code)


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
                    "result": {"success": False, "error": "Invalid data", "message": "Detailed error message"},
                    "name": "check_send_money_status",
                    "code": 1,
                    "version": "5.0.0",
                }
            },
        },
    },
    deprecated=True,
)
class OldCheckSendMoneyStatusView(BaseCheckSendMoneyStatusView):
    serializer_class = CheckSendMoneyStatusSerializer
    permission_classes = (HasValidAppCredentials,)


@extend_schema(
    tags=["Orchestration-Payments"],
    summary="Check Send Money Status",
    description=(
        "This endpoint checks the status of a money sending operation. "
        "The user can provide the operation ID and sender ID to get the current status."
    ),
    request=BaseCheckSendMoneyStatusSerializer,
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
                    "result": {"success": False, "error": "Invalid data", "message": "Detailed error message"},
                    "name": "check_send_money_status",
                    "code": 1,
                    "version": "5.0.0",
                }
            },
        },
    },
)
class CheckSendMoneyStatusView(BaseCheckSendMoneyStatusView):
    serializer_class = BaseCheckSendMoneyStatusSerializer
    permission_classes = (HasValidAppCredentialsV2,)


@IsValidGenericApi()
class BaseAcceptPayment(GenericAPIView):
    def post(self, request, serializer):
        accept_payment_data = serializer.validated_data
        app: FlouciApp = request.application
        if app.test:
            flouci_otp = serializer.validated_data["flouci_otp"]
            if flouci_otp == "F-111111":
                return Response({"result": {"status": "SUCCESS"}, "code": 0}, status=status.HTTP_200_OK)
            if flouci_otp == "F-000000":
                return Response({"result": {"status": "FAILED"}, "code": 0}, status=status.HTTP_200_OK)
        accept_payment_data["app_id"] = app.app_id
        accept_payment_data["destination"] = app.wallet
        accept_payment_data["app_token"] = app.public_token

        response = DataApiClient.accept_payment(data=accept_payment_data)
        return Response(response, status=response.get("status_code"))


@IsValidGenericApi()
class ConfirmSMTPreAuthorization(GenericAPIView):
    permission_classes = (HasValidAppCredentials | HasValidAppCredentialsV2,)
    serializer_class = ConfirmSMTPreAuthorizationSerializer

    def post(self, request, serializer):
        merchant_id = request.application.merchant_id
        payment_id = serializer.validated_data["payment_id"]
        amount = serializer.validated_data["amount"]
        response = FlouciBackendClient.confirm_payment(payment_id, amount, merchant_id)
        if response["success"]:
            data = {
                "result": {
                    "status": True,
                    "message": response.get("message"),
                    "payment_id": payment_id,
                },
                "name": "confirm_transaction",
                "code": 0,
                "version": DJANGO_SERVICE_VERSION,
            }
        else:
            data = {
                "result": {
                    "success": False,
                    "error": response.get("message") or response.get("error"),
                    "code": response.get("resultCode"),
                },
                "name": "confirm_transaction",
                "code": 1,
                "version": DJANGO_SERVICE_VERSION,
            }
        return Response(data=data, status=response.get("status_code"))


@IsValidGenericApi()
class CancelSMTPreAuthorization(GenericAPIView):
    permission_classes = (HasValidAppCredentials | HasValidAppCredentialsV2,)
    serializer_class = CancelSMTPreAuthorizationSerializer

    def post(self, request, serializer):
        merchant_id = request.application.merchant_id
        payment_id = serializer.validated_data["payment_id"]
        response = FlouciBackendClient.cancel_payment(payment_id, merchant_id)
        if response["success"]:
            data = {
                "result": {
                    "status": True,
                    "message": response.get("message"),
                    "payment_id": payment_id,
                },
                "name": "cancel_transaction",
                "code": 0,
                "version": DJANGO_SERVICE_VERSION,
            }
        else:
            data = {
                "result": {
                    "success": False,
                    "error": response.get("message") or response.get("error"),
                    "code": response.get("resultCode"),
                },
                "name": "cancel_transaction",
                "code": 1,
                "version": DJANGO_SERVICE_VERSION,
            }
        return Response(data=data, status=response.get("status_code"))


@extend_schema(
    tags=["Orchestration-Payments"],
    summary="Accept Money Status",
    description=("This endpoint accept payment. "),
    request=SecureAcceptPaymentSerializer,
    responses={
        200: {
            "description": "Send money successfully",
            "examples": {"application/json": {"result": {"status": "SUCCESS"}, "code": 0}},
        },
        400: {
            "description": "Invalid request data",
            "examples": {"application/json": {"result": {"status": "FAILED"}, "code": 1}},
        },
    },
    deprecated=True,
)
class AcceptPayment(BaseAcceptPayment):
    permission_classes = (HasValidAppCredentials,)
    serializer_class = SecureAcceptPaymentSerializer


@extend_schema(
    tags=["Orchestration-Payments"],
    summary="Accept Money Status",
    description=("This endpoint accept payment. "),
    request=AcceptPaymentSerializer,
    responses={
        200: {
            "description": "Send money successfully",
            "examples": {"application/json": {"result": {"status": "SUCCESS"}, "code": 0}},
        },
        400: {
            "description": "Invalid request data",
            "examples": {"application/json": {"result": {"status": "FAILED"}, "code": 1}},
        },
    },
)
class AcceptPaymentView(BaseAcceptPayment):
    permission_classes = (HasValidAppCredentialsV2,)
    serializer_class = AcceptPaymentSerializer
