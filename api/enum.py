from enum import Enum


class BaseEnum(Enum):
    @classmethod
    def get_choices(cls):
        return [(member.value, member.name) for member in cls]


class AppStatus(BaseEnum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"


class UserType(BaseEnum):
    INDIVIDUAL = "Individual"
    MERCHANT = "Merchant"


class CurrencyEnum(BaseEnum):
    TND = "TND"
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"


class PaymentMethod(BaseEnum):
    NFC = "nfc"
    CARD = "card"
    WALLET = "wallet"
    CHEQUE = "cheque"
