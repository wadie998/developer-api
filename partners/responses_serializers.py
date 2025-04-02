from rest_framework import serializers


class DefaultSerializer(serializers.Serializer):
    def create(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass


class BaseResponseSerializer(DefaultSerializer):
    success = serializers.BooleanField()
    message = serializers.CharField()


class IsFlouciResponseSerializer(DefaultSerializer):
    success = serializers.BooleanField()
    is_flouci = serializers.BooleanField()


class InitiateLinkAccounResponseSerializer(BaseResponseSerializer):
    phone_number = serializers.CharField()
    session_id = serializers.CharField()
    name = serializers.CharField()
    phone_number = serializers.CharField()


class PartnerInitiatePaymentResponseSerializer(BaseResponseSerializer):
    blockchain_ref = serializers.CharField()


class ConfirmLinkAccountResponseSerializer(BaseResponseSerializer):
    tracking_id = serializers.UUIDField()


class BalanceResponseSerializer(DefaultSerializer):
    success = serializers.BooleanField()
    wallet_id = serializers.CharField()
    balance_in_millimes = serializers.IntegerField()


class AccountBalanceNotFoundSerializer(DefaultSerializer):
    success = serializers.BooleanField()
    type = serializers.ChoiceField(choices=["M", "I"], required=False)
    is_ppa = serializers.BooleanField(required=False)
