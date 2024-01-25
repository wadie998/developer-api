import hmac
from hashlib import sha256

import bcrypt


def signed_request_is_valid(request, secret):
    """Validate signed requests."""
    api_signature = request.META.get("HTTP_SIGNATURE")
    if api_signature:
        request_check_field = request.data.get("id")
        if request_check_field is None:
            return False
        signature = generate_request_signature(secret, request.method, request.path, request_check_field)
        return signature == api_signature
    else:
        return False


def generate_request_signature(secret, request_method, request_path, request_check_field):
    params = [secret, request_method, request_path, request_check_field]
    formatted_data = "-".join(params)
    formatted_data = formatted_data.encode("utf-8")
    return hmac.new(secret.encode("utf-8"), msg=formatted_data, digestmod=sha256).hexdigest()


def verify_password_with_hash(password, hashed):
    if bcrypt.checkpw(password, hashed):
        return True
    else:
        return False


def hash_password(password):
    salt = bcrypt.gensalt(rounds=10, prefix=b"2a")
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password
