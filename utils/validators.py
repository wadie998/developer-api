import re

from rest_framework.exceptions import ValidationError

from api.constant import BASE64_IMAGE_REGEX


def validate_base64_image(value):
    if not re.match(BASE64_IMAGE_REGEX, value):
        raise ValidationError("Invalid Image format.")
    try:
        header_img, bare_img64 = value.split(",")
    except ValueError:
        raise ValidationError("Invalid base64 image format")
    if header_img == "":
        return bare_img64, "png", "image/png"
    elif header_img not in ("data:image/jpg;base64", "data:image/jpeg;base64", "data:image/png;base64"):
        raise ValidationError(f"Unsupported image type: {header_img}")
