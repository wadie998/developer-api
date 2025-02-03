import base64
import logging

import jwt
from django.utils import timezone

from settings.configs.jwt_config import JWT_EXPIRATION_DELTA
from settings.settings import BACKEND_JWT_PUBLIC_KEY, JWT_SECRET_KEY

logger = logging.getLogger(__name__)


def verify_backend_token(token, token_type="access", public_key=BACKEND_JWT_PUBLIC_KEY):
    """
    :param token:
    :param token_type:
    :return:
        - True, dict of extra jwt variables
        - False, None : expired token or wrong format
    """
    try:
        decoded = jwt.decode(token, public_key, options={"verify_exp": True, "require": ["exp"]}, algorithms=["ES256"])
        assert decoded["type"] == token_type
        return True, {key: val for key, val in decoded.items() if key not in ["exp", "iat", "type"]}
    except jwt.ExpiredSignatureError:
        return False, None
    except Exception as e:
        logger.warning("error verifying jwt token: %s", e)
        return False, None


def verify_jhipster_token(token, token_type="developer", public_key=BACKEND_JWT_PUBLIC_KEY):
    """
    :param token:
    :param token_type:
    :return:
        - True, dict of extra jwt variables
        - False, None : expired token or wrong format
    """
    try:
        decoded = jwt.decode(token, public_key, options={"verify_exp": True, "require": ["exp"]}, algorithms=["ES256"])
        assert decoded["type"] == token_type
        return True, {key: val for key, val in decoded.items() if key not in ["exp", "iat", "type"]}
    except jwt.ExpiredSignatureError:
        return False, None
    except Exception as e:
        logger.warning("error verifying jwt token: %s", e)
        return False, None


def verify_token(token, token_type="access", public_key=JWT_SECRET_KEY):
    """
    :param token:
    :param token_type:
    :return:
        - True, dict of extra jwt variables
        - False, None : expired token or wrong format
    """
    try:
        decoded = jwt.decode(token, base64.b64decode(JWT_SECRET_KEY), algorithms=["HS512"])
        return True, {key: val for key, val in decoded.items() if key not in ["exp", "iat", "type"]}
    except jwt.ExpiredSignatureError:
        return False, None
    except Exception as e:
        logger.warning("error verifying jwt token: %s", e)
        return False, None


def generate_token(user, auth):
    payload = {
        "sub": user,
        "auth": auth,
        "exp": timezone.now() + JWT_EXPIRATION_DELTA,
    }
    return jwt.encode(payload, base64.b64decode(JWT_SECRET_KEY), algorithm="HS512", headers={"typ": None})
