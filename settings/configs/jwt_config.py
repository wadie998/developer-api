from settings.configs.env import config

"""JWT"""

BACKEND_JWT_PUBLIC_KEY = config("BACKEND_JWT_PUBLIC_KEY", cast=lambda key: bytes(key.replace("\\n", "\n"), "utf-8"))
