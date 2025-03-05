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


class Currency(BaseEnum):
    TND = "TND"
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"


class SendMoneyServiceOperationTypes(BaseEnum):
    P2P = "P2P"
    PAYMENT = "PAYMENT"
    TOPUP = "TOPUP"
    GIFTCARD = "GIFTCARD"
    BILL_PAYMENT = "BILL_PAYMENT"
    DEVELOPER_API = "DEVELOPER_API"


class PartnerProducts(BaseEnum):
    TOPUP = "001"
    DATA_OPTION = "002"
    BILL_PAYMENT = "003"
    ECOMMERCE = "004"
    VAS = "005"


class TransactionsTypes(BaseEnum):
    P2P = "P2P"
    MERCHANT = "MERCHANT"


# TODO: Make them caps once updated by backend & front
class PaymentMethod(BaseEnum):
    NFC = "nfc"
    CARD = "card"
    WALLET = "wallet"
    CHECK = "check"


class RequestStatus:
    APPROVED = "A"
    DECLINED = "D"
    PENDING = "P"
    EXPIRED = "E"
    DATA_API_PENDING = "DP"
    DATA_API_CONFIRMED = "DC"
    WORKER_PENDING = "WP"
    DATA_API_FAILED = "DF"
    SERVICE_PENDING = "SP"
    SERVICE_FAILED = "SF"
    SERVICE_CONFIRMED = "SC"
    REFUND_PENDING = "RP"
    REFUND_FAILED = "RF"
    REFUND_CONFIRMED = "RC"

    @staticmethod
    def get_choices():
        return (
            (RequestStatus.APPROVED, "Approved"),
            (RequestStatus.DECLINED, "Declined"),
            (RequestStatus.PENDING, "Pending"),
            (RequestStatus.EXPIRED, "Expired"),
            (RequestStatus.DATA_API_PENDING, "DATA_API_PENDING"),
            (RequestStatus.DATA_API_CONFIRMED, "DATA_API_CONFIRMED"),
            (RequestStatus.DATA_API_FAILED, "DATA_API_FAILED"),
            (RequestStatus.SERVICE_PENDING, "SERVICE_PENDING"),
            (RequestStatus.SERVICE_FAILED, "SERVICE_FAILED"),
            (RequestStatus.SERVICE_CONFIRMED, "SERVICE_CONFIRMED"),
            (RequestStatus.REFUND_PENDING, "REFUND_PENDING"),
            (RequestStatus.REFUND_FAILED, "REFUND_FAILED"),
            (RequestStatus.REFUND_CONFIRMED, "REFUND_CONFIRMED"),
            (RequestStatus.WORKER_PENDING, "WORKER_PENDING"),
        )
