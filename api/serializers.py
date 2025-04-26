from rest_framework import serializers

from api.enum import Currency
from api.models import FlouciApp
from utils.image_helper import extract_base64_image_data
from utils.validators import validate_base64_image


class DefaultSerializer(serializers.Serializer):
    def create(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass


class Base64ImageField(serializers.CharField):
    """
    Custom field for validating and processing base64 encoded images.
    """

    def __init__(self, **kwargs):
        # Add the base64 image validator
        kwargs["validators"] = kwargs.get("validators", []) + [validate_base64_image]
        super().__init__(**kwargs)

    def validate(self, value):
        image_data, extension, content_type = extract_base64_image_data(value)
        return {
            "image_data": image_data,
            "extension": extension,
            "content_type": content_type,
        }


class AppCredsSerializer(DefaultSerializer):
    app_token = serializers.UUIDField()
    app_secret = serializers.UUIDField()


class AppInfoSerializer(DefaultSerializer):
    public_token = serializers.UUIDField()
    private_token = serializers.UUIDField()


class PartnerConnectedAppsSerializer(DefaultSerializer):
    pass


class UpdateConnectedAppsSerializer(DefaultSerializer):
    public_token = serializers.UUIDField()


class DestinationSerializer(DefaultSerializer):
    amount = serializers.IntegerField(min_value=1)
    destination = serializers.CharField(max_length=255)


class GeneratePaymentSerializer(DefaultSerializer):
    amount = serializers.IntegerField(min_value=100, max_value=2000000)
    accept_card = serializers.BooleanField()
    session_timeout_secs = serializers.IntegerField(default=1200)
    session_timeout = serializers.IntegerField(default=1200)
    success_link = serializers.URLField()
    fail_link = serializers.URLField()
    developer_tracking_id = serializers.CharField(min_length=1, max_length=50)
    accept_edinar = serializers.BooleanField(required=False)
    currency = serializers.ChoiceField(choices=Currency.get_choices(), default=Currency.TND.value)
    webhook = serializers.URLField(required=False)
    destination = DestinationSerializer(many=True, required=False)
    pre_authorization = serializers.BooleanField(default=False)

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
    imageBase64 = Base64ImageField(required=False)

    def validate(self, data):
        data["tracking_id"] = data["username"]
        image_info = data.get("imageBase64")
        if image_info:
            data["image_info"] = image_info
        return data


class ImageUpdateSerializer(DefaultSerializer):
    app_id = serializers.UUIDField()
    new_image = Base64ImageField()

    def validate(self, attrs):
        try:
            app = FlouciApp.objects.get(app_id=attrs["app_id"])
        except FlouciApp.DoesNotExist:
            raise serializers.ValidationError("App does not exist")
        attrs["app"] = app
        attrs["image_info"] = attrs["new_image"]

        return attrs


class UpdateDeveloperAppSerializer(DefaultSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField(min_length=3, max_length=100, required=False)
    description = serializers.CharField(min_length=3, max_length=255, required=False)


class BaseSendMoneySerializer(DefaultSerializer):
    amount = serializers.IntegerField(
        min_value=100, max_value=2000000
    )  # To verify with Anis, Should we consider packs/limits
    destination = serializers.CharField(max_length=35)
    webhook = serializers.URLField()

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


class ConfirmSMTPreAuthorizationSerializer(DefaultSerializer):
    payment_id = serializers.CharField()
    amount = serializers.IntegerField()


class CancelSMTPreAuthorizationSerializer(DefaultSerializer):
    payment_id = serializers.CharField()
