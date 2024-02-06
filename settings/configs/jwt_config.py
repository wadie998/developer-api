from decouple import config

"""JWT"""

BACKEND_JWT_PUBLIC_KEY = config("BACKEND_JWT_PUBLIC_KEY", cast=lambda key: bytes(key.replace("\\n", "\n"), "utf-8"))
JWT_PROJECT_PRIVATE_KEY = config(
    "JWT_PROJECT_PRIVATE_KEY", cast=lambda key: bytes(key.replace("\\n", "\n"), "utf-8"), default=""
)
JWT_PROJECT_PUBLIC_KEY = config(
    "JWT_PROJECT_PUBLIC_KEY", cast=lambda key: bytes(key.replace("\\n", "\n"), "utf-8"), default=""
)
PROJECT_VERIFICATION_TOKEN = config("PROJECT_VERIFICATION_TOKEN", default="")
