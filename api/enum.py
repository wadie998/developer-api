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
