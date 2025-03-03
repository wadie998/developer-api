import requests
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from api.enum import RequestStatus
from api.permissions import HasValidDataApiSignature
from partners.serializers import DevAPIDataApiCatcherSerializer
from utils.decorators import IsValidGenericApi


@IsValidGenericApi()
class SendMoneyDeveloperApiCatcher(GenericAPIView):
    permission_classes = (HasValidDataApiSignature,)
    serializer_class = DevAPIDataApiCatcherSerializer

    def post(self, request, serializer):
        operation = serializer.validated_data.get("transaction")

        if not serializer.validated_data["result"]["success"]:
            operation.set_operation_status(RequestStatus.DECLINED)
            return Response(
                data={"success": False, "message": f"Operation {operation.uuid} aborted"},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )
        operation.set_operation_status(RequestStatus.APPROVED)
        operation.blockchain_ref = serializer.validated_data["result"]["transactionId"]
        operation.save(update_fields=["blockchain_ref"])
        if operation.operation_payload.get("webhook"):
            # TODO make this a task
            headers = {"Content-Type": "application/json"}
            response_data = {
                "success": True,
                "operation_id": str(operation.operation_id),
            }
            developer_webhook_url = (
                f"{operation.operation_payload.get('webhook_url')}?payment_id={operation.operation_id}"
            )
            try:
                response = requests.get(developer_webhook_url, params=response_data, headers=headers, timeout=10)
                if response:
                    operation.operation_payload.update({"webhook_sent": True})
                    operation.save(update_fields=["operation_payload"])
            except requests.RequestException:
                pass
        return Response(
            data={"success": True, "message": f"Operation {operation.operation_id} validated"},
            status=status.HTTP_200_OK,
        )
