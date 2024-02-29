from datetime import timedelta

from settings.configs.env import config

"""JWT"""

BACKEND_JWT_PUBLIC_KEY = config("BACKEND_JWT_PUBLIC_KEY", cast=lambda key: bytes(key.replace("\\n", "\n"), "utf-8"))
JWT_SECRET_KEY = config("JWT_SECRET_KEY", default="")
JWT_EXPIRATION_DELTA = timedelta(minutes=15)
