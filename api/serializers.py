import base64

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from rest_framework import serializers

from api.models import FlouciApp


class DefaultSerializer(serializers.Serializer):
    def create(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass


class GeneratePaymentSerializer(DefaultSerializer):
    app_token = serializers.UUIDField()
    app_secret = serializers.UUIDField()
    amount = serializers.IntegerField(min_value=100, max_value=5000000)
    accept_card = serializers.BooleanField()
    session_timeout_secs = serializers.IntegerField(min_value=300, default=1200)
    session_timeout = serializers.IntegerField(min_value=300, default=1200)
    success_link = serializers.URLField()
    fail_link = serializers.URLField()
    developer_tracking_id = serializers.CharField(max_length=100)
    accept_edinar = serializers.BooleanField(required=False)
    currency = serializers.CharField(required=False)
    webhook = serializers.URLField(required=False)
    destination = serializers.ListField(child=serializers.JSONField(), required=False)

    def validate(self, validate_data):
        try:
            application = FlouciApp.objects.get(
                public_token=validate_data.get("app_token"), private_token=validate_data.get("app_secret")
            )
        except ObjectDoesNotExist:
            raise serializers.ValidationError("App not found.")
        if "destination" in validate_data:
            for item in validate_data["destination"]:
                if not isinstance(item, dict) or "amount" not in item or "destination" not in item:
                    raise serializers.ValidationError(
                        "Each item in the destination field must be a JSON object with 'amount' and 'destination' keys."
                    )
        validate_data["merchant_id"] = application.merchant_id
        validate_data["test"] = application.test
        validate_data["webhook"] = validate_data.get("webhook", None)
        validate_data["currency"] = validate_data.get("currency", "TND")
        validate_data["amount_in_millimes"] = validate_data.get("amount")
        return validate_data


class VerifyPaymentSerializer(DefaultSerializer):
    payment_id = serializers.CharField(max_length=100)


class CheckUserExistsSerializer(DefaultSerializer):
    tracking_id = serializers.CharField()


class CreateDeveloperAccountSerializer(DefaultSerializer):
    login = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=50)
    firstName = serializers.CharField(max_length=50)
    lastName = serializers.CharField(max_length=50, required=False)
    email = serializers.EmailField(required=False)


class GetDeveloperAppSerializer(DefaultSerializer):
    pass


class CreateDeveloperAppSerializer(DefaultSerializer):
    name = serializers.CharField(min_length=3, max_length=100)
    description = serializers.CharField(min_length=3, max_length=255)
    merchant_id = serializers.CharField(max_length=255)
    wallet = serializers.CharField(max_length=255)
    username = serializers.CharField()
    imageBase64 = serializers.CharField(required=False)

    def validate(self, data):
        app_image = data.get("imageBase64")
        if app_image:
            try:
                # Decode the base64 string
                format, imgstr = app_image.split(";base64,")
                ext = format.split("/")[-1]  # Extract the file extension
                img_data = base64.b64decode(imgstr)

                # Check the size of the image
                if len(img_data) > 3 * 1024 * 1024:  # 3 MB
                    raise serializers.ValidationError("Image size must be less than 3 MB.")

                # Optionally, you can save the image to a file or perform further validation
                data["app_image"] = ContentFile(img_data, name=f"temp.{ext}")
            except (ValueError, TypeError, base64.binascii.Error):
                raise serializers.ValidationError("Invalid base64 image string.")
        data["tracking_id"] = data.get("username")
        return data


class SendMoneySerializer(DefaultSerializer):
    amount = serializers.IntegerField(
        min_value=100, max_value=5000000
    )  # To verify with Anis, Should we consider packs/limits
    destination = serializers.CharField(max_length=15)
    app_secret = serializers.UUIDField()
    app_token = serializers.UUIDField()
    webhook = serializers.URLField(required=False)

    def validate(self, data):
        if data["amount_in_millimes"] <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return data


class CheckSendMoneyStatusSerializer(DefaultSerializer):
    app_secret = serializers.UUIDField()
    app_token = serializers.UUIDField()
    operation_id = serializers.UUIDField()


class AcceptPaymentSerializer(serializers.Serializer):
    flouci_otp = serializers.CharField(required=True)
    app_token = serializers.CharField(required=True)
    payment_id = serializers.CharField(required=True)
    app_id = serializers.UUIDField(required=False, default=None)
    amount = serializers.IntegerField(required=True)
    destination = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    developer_tracking_id = serializers.CharField(required=False, allow_null=True, max_length=255)


class SecureAcceptPaymentSerializer(AcceptPaymentSerializer):
    app_secret = serializers.CharField(required=True)
