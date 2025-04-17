import re

from rest_framework.exceptions import ValidationError

from api.constant import BASE64_IMAGE_REGEX


def validate_base64_image(value):
    if not re.match(BASE64_IMAGE_REGEX, value):
        raise ValidationError("Invalid Image format.")
