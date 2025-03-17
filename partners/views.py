from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from api.enum import RequestStatus, SendMoneyServiceOperationTypes
from api.permissions import (
    HasValidPartnerAppCredentials,
    IsPartnerAuthenticated,
    IsValidPartnerUser,
)
from partners.models import LinkedAccount, PartnerTransaction
from partners.serializers import (
    AuthenticateViewSerializer,
    BalanceViewSerializer,
    ConfirmLinkAccountViewSerializer,
    FilterHistorySerializer,
    InitiateLinkAccountViewSerializer,
    InitiatePaymentViewSerializer,
    InitiatePosTransactionSerializer,
    IsFlouciViewSerializer,
    PaginatedHistorySerializer,
    PartnerBalanceViewSerializer,
    PartnerFilterHistorySerializer,
    PartnerInitiatePaymentViewSerializer,
    RefreshAuthenticateViewSerializer,
    SendMoneyViewSerializer,
)
from utils.backend_client import FlouciBackendClient
from utils.decorators import IsValidGenericApi


@IsValidGenericApi()
class InitiateLinkAccountView(GenericAPIView):
    permission_classes = [HasValidPartnerAppCredentials]
    serializer_class = InitiateLinkAccountViewSerializer

    def post(self, request, serializer):
        phone_number = serializer.validated_data.get("phone_number")
        if LinkedAccount.objects.filter(
            phone_number=phone_number,
            merchant_id=request.application.merchant_id,
        ).exists():
            return Response({"success": False, "message": "Account already linked."}, status=status.HTTP_202_ACCEPTED)
        response = FlouciBackendClient.initiate_link_account(
            phone_number=phone_number, merchant_id=request.application.merchant_id
        )

        status_code = response.get("status_code")
        # response = response.json()
        if response.get("success"):
            if response["body"].get("tracking_id"):
                tracking_id = response["body"].get("tracking_id")
                if LinkedAccount.objects.filter(
                    account_tracking_id=tracking_id,
                    merchant_id=request.application.merchant_id,
                ).exists():
                    return Response(
                        {"success": False, "message": "Account already linked."}, status=status.HTTP_202_ACCEPTED
                    )
            return Response(
                data={
                    "success": True,
                    "session_id": response["body"].get("session_id"),
                    "name": response["body"].get("name"),
                    "phone_number": response["body"].get("phone_number"),
                    "message": response.get("message"),
                },
                status=status_code,
            )
        else:
            return Response({"success": False, "message": "Unexpected error occurred"}, status=status_code)


@IsValidGenericApi()
class ConfirmLinkAccountView(GenericAPIView):
    permission_classes = [HasValidPartnerAppCredentials]
    serializer_class = ConfirmLinkAccountViewSerializer

    def post(self, request, serializer):
        phone_number = serializer.validated_data.get("phone_number")
        session_id = serializer.validated_data.get("session_id")
        otp = serializer.validated_data.get("otp")

        response = FlouciBackendClient.confirm_link_account(
            phone_number=phone_number,
            session_id=session_id,
            otp=otp,
            merchant_id=request.application.merchant_id,
        )
        if response.get("success"):
            account_link, _ = LinkedAccount.objects.get_or_create(
                phone_number=phone_number,
                account_tracking_id=response.get("tracking_id"),
                merchant_id=request.application.merchant_id,
            )
            return Response(
                data={
                    "success": True,
                    "tracking_id": str(account_link.partner_tracking_id),
                },
                status=response.get("status_code"),
            )
        else:
            return Response(
                {"success": False, "message": "Unexpected error occurred"}, status=response.get("status_code")
            )


@IsValidGenericApi()
class IsFlouciView(GenericAPIView):
    permission_classes = [HasValidPartnerAppCredentials]
    serializer_class = IsFlouciViewSerializer

    def post(self, request, serializer):
        phone_number = serializer.validated_data.get("phone_number")
        merchant_id = request.application.merchant_id
        response = FlouciBackendClient.is_flouci(
            phone_number=phone_number,
            merchant_id=merchant_id,
        )
        return Response(data=response, status=response.get("status_code"))


@IsValidGenericApi()
class AuthenticateView(GenericAPIView):
    permission_classes = [HasValidPartnerAppCredentials]
    serializer_class = AuthenticateViewSerializer

    def post(self, request, serializer):
        application_tracking_id = serializer.validated_data.get("tracking_id")
        phone_number = serializer.validated_data.get("phone_number")
        try:
            merchant_id = request.application.merchant_id
            linked_account = LinkedAccount.objects.get(
                partner_tracking_id=application_tracking_id, merchant_id=merchant_id
            )
        except ObjectDoesNotExist:
            return Response({"success": False, "message": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        response = FlouciBackendClient.generate_authentication_token(
            phone_number=phone_number,
            account_tracking_id=str(linked_account.account_tracking_id),
            partner_tracking_id=str(linked_account.partner_tracking_id),
            merchant_id=merchant_id,
        )
        return Response(data=response, status=response.get("status_code"))


class RefreshAuthenticateView(APIView):
    permission_classes = [IsPartnerAuthenticated]
    serializer_class = RefreshAuthenticateViewSerializer

    def post(self, request, seriazlier):
        # Logic for refreshing authentication
        return Response({"message": "Refresh authenticate"})


@IsValidGenericApi(post=False, get=True)
class BalanceView(GenericAPIView):
    permission_classes = [IsPartnerAuthenticated]
    serializer_class = BalanceViewSerializer

    def get(self, request, serializer):
        account: LinkedAccount = request.account
        response = FlouciBackendClient.get_user_balance(
            tracking_id=account.account_tracking_id,
        )
        return Response(data=response, status=response.get("status_code"))


@IsValidGenericApi(post=False, get=True)
class PartnerBalanceView(GenericAPIView):
    permission_classes = [HasValidPartnerAppCredentials, IsValidPartnerUser]
    serializer_class = PartnerBalanceViewSerializer

    def get(self, request, serializer):
        response = FlouciBackendClient.get_user_balance(
            tracking_id=request.account.account_tracking_id,
        )
        return Response(data=response, status=response.get("status_code"))


class HistoryPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class BaseRequestView(GenericAPIView):
    def get_filters(self, validated_data):
        """
        Build filters for the queryset based on the validated data.
        """
        filters = Q(Q(sender=self.request.account) | Q(receiver=self.request.account))

        from_date = validated_data.get("from_date")
        to_date = validated_data.get("to_date")

        operation_type = validated_data.get("operation_type")
        operation_status = validated_data.get("operation_status")

        if from_date:
            filters &= Q(time_created__gte=from_date)
        if to_date:
            filters &= Q(time_created__lte=to_date)
        if operation_type:
            filters &= Q(operation_type=operation_type)
        if operation_status:
            filters &= Q(operation_status=operation_status)

        return filters

    def get_filtered_queryset(self, serializer_class):
        """
        Apply filters to the queryset based on the validated data.
        """
        serializer = serializer_class(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        filters = self.get_filters(serializer.validated_data)
        return (
            PartnerTransaction.objects.filter(filters)
            .only("operation_status", "operation_payload", "amount_in_millimes", "sender", "receiver", "operation_id")
            .order_by("-time_created")
        )


@IsValidGenericApi(get=True, post=False)
class HistoryView(BaseRequestView, ListAPIView):
    """
    Display paginated history of transactions.
    """

    permission_classes = [IsPartnerAuthenticated]
    serializer_class = PaginatedHistorySerializer
    pagination_class = HistoryPagination

    def get_queryset(self):
        queryset = self.get_filtered_queryset(FilterHistorySerializer)
        page_size = self.request.query_params.get("size", self.pagination_class.page_size)
        self.pagination_class.page_size = min(int(page_size), self.pagination_class.max_page_size)
        return queryset


@IsValidGenericApi(post=False, get=True)
class PartnerHistoryView(BaseRequestView, ListAPIView):
    """
    Display paginated history of transactions.
    """

    permission_classes = [HasValidPartnerAppCredentials, IsValidPartnerUser]
    serializer_class = PaginatedHistorySerializer
    pagination_class = HistoryPagination

    def get_queryset(self):
        queryset = self.get_filtered_queryset(PartnerFilterHistorySerializer)
        page_size = self.request.query_params.get("size", self.pagination_class.page_size)
        self.pagination_class.page_size = min(int(page_size), self.pagination_class.max_page_size)
        return queryset


@IsValidGenericApi()
class InitiatePaymentView(GenericAPIView):
    permission_classes = [HasValidPartnerAppCredentials]
    serializer_class = InitiatePaymentViewSerializer

    # @method_decorator(ratelimit(key="user", rate="1/10s"))
    def post(self, request, serializer):
        account = request.account
        amount_in_millimes = serializer.validated_data.get("amount_in_millimes")
        merchant_id = request.account.merchant_id

        with transaction.atomic():
            operation = PartnerTransaction.objects.create(
                operation_type=SendMoneyServiceOperationTypes.PAYMENT,
                sender=account,
                operation_payload={
                    "merchant_id": merchant_id,
                    "product": serializer.validated_data.get("product"),
                    "webhook": serializer.validated_data.get("webhook"),
                },
                amount_in_millimes=amount_in_millimes,
                operation_status=RequestStatus.PENDING,
            )
        response = FlouciBackendClient.send_money(operation, merchant_id=merchant_id)
        if response.get("success"):
            operation.set_operation_status(RequestStatus.DATA_API_PENDING)
        else:
            operation.set_operation_status(RequestStatus.DECLINED)
        return Response(data=response, status=response.get("status_code"))


@IsValidGenericApi()
class PartnerInitiatePaymentView(GenericAPIView):
    permission_classes = [HasValidPartnerAppCredentials, IsValidPartnerUser]
    serializer_class = PartnerInitiatePaymentViewSerializer

    # @method_decorator(ratelimit(key="user", rate="1/10s"))
    def post(self, request, serializer):
        account = request.account
        amount_in_millimes = serializer.validated_data.get("amount_in_millimes")
        merchant_id = request.account.merchant_id

        with transaction.atomic():
            operation = PartnerTransaction.objects.create(
                operation_type=SendMoneyServiceOperationTypes.PAYMENT,
                sender=account,
                operation_payload={
                    "merchant_id": merchant_id,
                    "product": serializer.validated_data.get("product"),
                    "webhook": serializer.validated_data.get("webhook"),
                },
                amount_in_millimes=amount_in_millimes,
                operation_status=RequestStatus.PENDING,
            )
        response = FlouciBackendClient.send_money(operation, merchant_id=merchant_id)
        if response.get("success"):
            operation.set_operation_status(RequestStatus.DATA_API_PENDING)
        else:
            operation.set_operation_status(RequestStatus.DECLINED)

        response_data = {key: value for key, value in response.items() if key != "hash"}
        response_data["operation_id"] = str(operation.operation_id)
        return Response(data=response_data, status=response.get("status_code"))


@IsValidGenericApi()
class InitiatePosTransaction(GenericAPIView):
    permission_classes = (HasValidPartnerAppCredentials,)
    serializer_class = InitiatePosTransactionSerializer

    def post(self, request, serializer):
        app = request.application
        merchant_id = app.merchant_id
        response = FlouciBackendClient.generate_pos_transaction(
            merchant_id=merchant_id,
            webhook_url=serializer.validated_data["webhook"],
            id_terminal=serializer.validated_data["id_terminal"],
            serial_number=serializer.validated_data["serial_number"],
            service_code=serializer.validated_data["service_code"],
            amount_in_millimes=serializer.validated_data["amount_in_millimes"],
            payment_method=serializer.validated_data["payment_method"],
        )
        return Response(response, status=response.get("status_code", 200))


class PartnerSendMoneyView(GenericAPIView):
    permission_classes = [IsPartnerAuthenticated]
    serializer_class = SendMoneyViewSerializer

    def post(self, request, serializer):
        # Logic for sending money
        return Response({"message": "Send money"})
