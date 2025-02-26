import logging

import jwt

from settings.configs.jwt_config import BACKEND_JWT_PUBLIC_KEY

logger = logging.getLogger(__name__)


def verify_backend_token(token, token_type="partner", public_key=BACKEND_JWT_PUBLIC_KEY):
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
        logger.warning(f"Error verifying jwt token:{e}")
        return False, None
