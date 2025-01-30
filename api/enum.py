from enum import Enum


class AppStatus(Enum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"

    @staticmethod
    def get_choices():
        return ((tag.value, tag.name) for tag in AppStatus)
