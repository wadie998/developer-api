from enum import Enum


class AppStatus(Enum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"

    @staticmethod
    def get_choices():
        return ((tag.value, tag.name) for tag in AppStatus)


class UserType(Enum):
    Individual = "Individual"
    Merchant = "Merchant"

    @staticmethod
    def get_choices():
        return ((tag.value, tag.name) for tag in UserType)


class CurrencyEnum(Enum):
    TND = "TND"
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"

    @staticmethod
    def get_choices():
        return ((tag.value, tag.name) for tag in CurrencyEnum)


class PaymentMethod(Enum):
    NFC = "NFC"
    CARD = "CARD"
    WALLET = "WALLET"
    CHEQUE = "CHEQUE"

    @staticmethod
    def get_choices():
        return ((tag.value, tag.name) for tag in PaymentMethod)
