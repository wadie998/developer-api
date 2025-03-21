import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from api.enum import Currency


class DefaultSerializer(serializers.Serializer):
    def create(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass


class AppCredsSerializer(DefaultSerializer):
    app_token = serializers.UUIDField()
    app_secret = serializers.UUIDField()


class DestinationSerializer(DefaultSerializer):
    amount = serializers.IntegerField(min_value=1)
    destination = serializers.CharField(max_length=255)


class GeneratePaymentSerializer(DefaultSerializer):
    amount = serializers.IntegerField(min_value=100, max_value=5000000)
    accept_card = serializers.BooleanField()
    session_timeout_secs = serializers.IntegerField(min_value=300, default=1200)
    session_timeout = serializers.IntegerField(min_value=300, default=1200)
    success_link = serializers.URLField()
    fail_link = serializers.URLField()
    developer_tracking_id = serializers.CharField(max_length=40)
    accept_edinar = serializers.BooleanField(required=False)
    currency = serializers.ChoiceField(choices=Currency.get_choices(), default=Currency.TND.value)
    webhook = serializers.URLField(required=False)
    destination = DestinationSerializer(many=True, required=False)

    def validate(self, validate_data):
        application = self.context.get("request").application
        validate_data["merchant_id"] = application.merchant_id
        validate_data["test"] = application.test
        validate_data["webhook"] = validate_data.get("webhook", None)
        validate_data["amount_in_millimes"] = validate_data.get("amount")
        return validate_data


class OldGeneratePaymentSerializer(AppCredsSerializer, GeneratePaymentSerializer):
    pass


class VerifyPaymentSerializer(DefaultSerializer):
    payment_id = serializers.CharField(max_length=100)


class CheckUserExistsSerializer(DefaultSerializer):
    tracking_id = serializers.UUIDField()

    def validate(self, validate_data):
        tracking_id = self.context.get("request").tracking_id
        if tracking_id and tracking_id != str(validate_data["tracking_id"]):
            raise serializers.ValidationError("Bad input")
        return validate_data


class CreateDeveloperAccountSerializer(DefaultSerializer):
    login = serializers.CharField(max_length=100)


class GetDeveloperAppSerializer(DefaultSerializer):
    tracking_id = serializers.UUIDField(required=False)


class CreateDeveloperAppSerializer(DefaultSerializer):
    name = serializers.CharField(min_length=3, max_length=100)
    description = serializers.CharField(min_length=3, max_length=255, required=False)
    merchant_id = serializers.CharField(max_length=255)
    username = serializers.CharField()
    wallet = serializers.CharField(max_length=255)
    imageBase64 = serializers.CharField(required=False)

    def validate(self, data):
        data["tracking_id"] = data["username"]
        image_b64 = data.get("imageBase64")
        if image_b64:
            data["app_image"] = self._decode_base64_image(image_b64)

        return data

    def _decode_base64_image(self, image_b64):
        MAX_IMAGE_SIZE = 3 * 1024 * 1024  # 3 MB
        """Helper function to decode base64 image."""
        try:
            header, encoded = image_b64.split(";base64,")
            ext = header.rsplit("/", 1)[-1]  # Extract file extension
            img_data = base64.b64decode(encoded)
        except (ValueError, TypeError, base64.binascii.Error):
            raise serializers.ValidationError("Invalid base64 image string.")

        if len(img_data) > MAX_IMAGE_SIZE:
            raise serializers.ValidationError("Image size must be less than 3 MB.")

        return ContentFile(img_data, name=f"temp.{ext}")


class BaseSendMoneySerializer(DefaultSerializer):
    amount = serializers.IntegerField(
        min_value=100, max_value=5000000
    )  # To verify with Anis, Should we consider packs/limits
    destination = serializers.CharField(max_length=35)
    webhook = serializers.URLField(required=False)

    def validate(self, data):
        data["amount_in_millimes"] = data["amount"]
        return data


class SendMoneySerializer(BaseSendMoneySerializer, AppCredsSerializer):
    pass


class BaseCheckSendMoneyStatusSerializer(DefaultSerializer):
    operation_id = serializers.UUIDField()


class CheckSendMoneyStatusSerializer(BaseCheckSendMoneyStatusSerializer, AppCredsSerializer):
    pass


class AcceptPaymentSerializer(DefaultSerializer):
    flouci_otp = serializers.CharField()
    payment_id = serializers.CharField()
    app_id = serializers.UUIDField(required=False, default=None)
    amount = serializers.IntegerField()
    destination = serializers.CharField(required=False, max_length=40, allow_null=True, allow_blank=True)
    developer_tracking_id = serializers.CharField(required=False, allow_null=True, max_length=40)


class SecureAcceptPaymentSerializer(AcceptPaymentSerializer, AppCredsSerializer):
    pass


class DeveloperAppSerializer(DefaultSerializer):
    id = serializers.IntegerField()
