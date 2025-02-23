import logging
import re

from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)

meeting_slot_pattern = re.compile(r"^\d{1,2}-\d{1,2}-\d{4}T\d{1,2}-\d{2}$")


def is_valid_phone_number(number):
    """
    checks if phone number is a valid, 8 digit, Tunisian mobile number
    :param number:
    :return:
    """
    return number.isdigit() and len(number) == 8  # and (number[0] in PHONE_PREFIXES)


def validator_string_is_digit(string_to_test: str):
    if not string_to_test.isdigit():
        raise ValidationError("Should contains only digits")


def validator_string_is_phone_number(string_to_test: str):
    if not is_valid_phone_number(string_to_test):
        raise ValidationError("Invalid phone number")


def validator_string_is_peer_id(string_to_test: str):
    if not string_to_test.isdigit() or len(string_to_test) > 8:
        raise ValidationError("Invalid peer_id. must contain digits only")
