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


class SendMoneyServiceOperationTypes:
    P2P = "P2P"
    PAYMENT = "PAYMENT"
    TOPUP = "TOPUP"
    GIFTCARD = "GIFTCARD"
    BILL_PAYMENT = "BILL_PAYMENT"
    DEVELOPER_API = "DEVELOPER_API"

    @staticmethod
    def get_choices():
        return (
            (SendMoneyServiceOperationTypes.P2P, "P2P"),
            (SendMoneyServiceOperationTypes.PAYMENT, "PAYMENT"),
            (SendMoneyServiceOperationTypes.GIFTCARD, "GIFTCARD"),
            (SendMoneyServiceOperationTypes.TOPUP, "TOPUP"),
            (SendMoneyServiceOperationTypes.BILL_PAYMENT, "BILL_PAYMENT"),
            (SendMoneyServiceOperationTypes.DEVELOPER_API, "DEVELOPER_API"),
        )


class PartnerProducts:
    TOPUP = "001"
    DATA_OPTION = "002"
    BILL_PAYMENT = "003"
    ECOMMERCE = "004"
    VAS = "005"

    @staticmethod
    def get_choices():
        return (
            (PartnerProducts.TOPUP, "TOPUP"),
            (PartnerProducts.DATA_OPTION, "DATA_OPTION"),
            (PartnerProducts.BILL_PAYMENT, "BILL_PAYMENT"),
            (PartnerProducts.ECOMMERCE, "ECOMMERCE"),
            (PartnerProducts.VAS, "VAS"),
        )


class TransactionsTypes:
    P2P = "P2P"
    MERCHANT = "MERCHANT"

    @staticmethod
    def get_choices():
        return (
            (TransactionsTypes.P2P, "P2P"),
            (TransactionsTypes.MERCHANT, "MERCHANT"),
        )


class PaymentMethod:
    NFC = "NFC"
    CARD = "CARD"
    WALLET = "WALLET"
    CHECK = "CHECK"

    @staticmethod
    def get_choices():
        return (
            (PaymentMethod.NFC, "Nfc"),
            (PaymentMethod.CARD, "Card"),
            (PaymentMethod.WALLET, "Wallet"),
            (PaymentMethod.CHECK, "Check"),
        )
