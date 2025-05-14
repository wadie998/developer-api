from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from api.enum import (
    PartnerProducts,
    PaymentMethod,
    RequestStatus,
    SendMoneyServiceOperationTypes,
)
from partners.models import PartnerTransaction
from partners.validators import (
    validator_string_is_digit,
    validator_string_is_phone_number,
)


class DefaultSerializer(serializers.Serializer):
    def create(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass


class DefaultPartnerSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=8, min_length=8, validators=[validator_string_is_phone_number])
    tracking_id = serializers.UUIDField()


class IsFlouciSerializer(DefaultSerializer):
    phone_number = serializers.CharField(max_length=8, min_length=8, validators=[validator_string_is_phone_number])


class InitiateLinkAccountSerializer(DefaultSerializer):
    phone_number = serializers.CharField(max_length=8, min_length=8, validators=[validator_string_is_phone_number])


class ConfirmLinkAccountSerializer(DefaultSerializer):
    phone_number = serializers.CharField(max_length=8, min_length=8, validators=[validator_string_is_phone_number])
    session_id = serializers.UUIDField()
    otp = serializers.CharField(max_length=6, min_length=6, validators=[validator_string_is_digit])


class AuthenticateSerializer(DefaultSerializer):
    phone_number = serializers.CharField(max_length=8, min_length=8, validators=[validator_string_is_phone_number])
    tracking_id = serializers.UUIDField()


class RefreshAuthenticateSerializer(DefaultSerializer):
    pass


class BalanceSerializer(DefaultSerializer):
    pass


class PartnerBalanceSerializer(DefaultPartnerSerializer):
    pass


class PaginatedHistorySerializer(serializers.ModelSerializer):
    payload = serializers.SerializerMethodField()
    sender = serializers.CharField(source="sender.phone_number", read_only=True)
    receiver = serializers.CharField(source="receiver.phone_number", read_only=True)
    status = serializers.CharField(source="get_operation_status_display", read_only=True)

    class Meta:
        model = PartnerTransaction
        fields = ["operation_id", "sender", "receiver", "status", "time_created", "payload"]

    @extend_schema_field(serializers.JSONField())  # Explicitly specify the schema type
    def get_payload(self, obj):
        payload = obj.operation_payload or {}
        return {
            "blockchain_ref": obj.blockchain_ref[:6] if obj.blockchain_ref else None,
            "operation_type": obj.operation_type,
            "product": payload.get("product", ""),
        }


class BaseRequestViewSerializer(serializers.Serializer):
    from_date = serializers.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M:%SZ"],
        default=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0),
    )
    to_date = serializers.DateTimeField(input_formats=["%Y-%m-%dT%H:%M:%SZ"], default=timezone.now)
    operation_type = serializers.ChoiceField(choices=SendMoneyServiceOperationTypes.get_choices(), required=False)
    operation_status = serializers.ChoiceField(choices=RequestStatus.get_choices(), default=RequestStatus.APPROVED)


class FilterHistorySerializer(BaseRequestViewSerializer):
    page = serializers.IntegerField(min_value=1, default=1)
    size = serializers.IntegerField(min_value=1, max_value=10000, default=10)


class PartnerFilterHistorySerializer(DefaultPartnerSerializer, BaseRequestViewSerializer):
    page = serializers.IntegerField(min_value=1, default=1)
    size = serializers.IntegerField(min_value=1, max_value=10000, default=10)


class InitiatePaymentViewSerializer(DefaultSerializer):
    amount_in_millimes = serializers.IntegerField(min_value=1000)
    product = serializers.ChoiceField(choices=PartnerProducts.get_choices())
    webhook = serializers.URLField(required=False)


class PartnerInitiatePaymentViewSerializer(DefaultPartnerSerializer):
    amount_in_millimes = serializers.IntegerField(min_value=1000)
    product = serializers.ChoiceField(choices=PartnerProducts.get_choices())
    webhook = serializers.URLField(required=False)


class SendMoneyViewSerializer(DefaultSerializer):
    pass


class DevAPIDataApiCatcherSerializer(DefaultSerializer):
    id = serializers.UUIDField()
    result = serializers.JSONField()

    def validate(self, data):
        operation_id = data.get("id")
        try:
            transaction = PartnerTransaction.objects.get(
                operation_id=operation_id, operation_status__in=[RequestStatus.DATA_API_PENDING]
            )
            data["transaction"] = transaction
        except PartnerTransaction.DoesNotExist:
            raise serializers.ValidationError({"id": "Transaction with this operation_id does not exist."})
        return data


class MultiPaymentItemSerializer(serializers.Serializer):
    amount_in_millimes = serializers.IntegerField(min_value=1000)
    payment_method = serializers.ChoiceField(choices=PaymentMethod.get_choices())
    developer_tracking_id = serializers.CharField(max_length=60)


class InitiatePosTransactionSerializer(DefaultSerializer):
    id_terminal = serializers.CharField(max_length=16)
    serial_number = serializers.CharField(max_length=36)
    service_code = serializers.CharField(max_length=3, required=False, default="024")
    is_multi_payment = serializers.BooleanField(default=False)
    payment_segments = MultiPaymentItemSerializer(many=True, required=False)

    # Fallback for single payment
    amount_in_millimes = serializers.IntegerField(min_value=1000, required=False)
    payment_method = serializers.ChoiceField(
        choices=PaymentMethod.get_choices(), default=PaymentMethod.CARD, required=False
    )
    developer_tracking_id = serializers.CharField(max_length=60, required=False)
    webhook = serializers.URLField(required=False)

    def validate(self, data):
        if data.get("is_multi_payment"):
            if not data.get("payment_segments"):
                raise serializers.ValidationError("payment_segments must be provided for multi-payment.")
        else:
            required_fields = ["amount_in_millimes", "payment_method", "developer_tracking_id"]
            missing = [f for f in required_fields if not data.get(f)]
            if missing:
                raise serializers.ValidationError(f"Missing required fields for single payment: {', '.join(missing)}")
        return data


class FetchPOSTransactionStatusSerializer(DefaultSerializer):
    developer_tracking_id = serializers.CharField(max_length=60, required=False)
    flouci_transaction_id = serializers.UUIDField(required=False)

    def validate(self, validate_data):
        transaction_id = validate_data.get("flouci_transaction_id")
        developer_tracking_id = validate_data.get("developer_tracking_id")
        if not transaction_id and not developer_tracking_id:
            raise serializers.ValidationError("Provide either 'flouci_transaction_id' or 'developer_tracking_id'.")
        return validate_data
