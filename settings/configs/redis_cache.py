from decouple import config

from settings.settings import INSTALLED_APPS

"""
Redis database parameters
"""
REDIS_ENABLED = config("REDIS_ENABLED", default=False, cast=bool)
if REDIS_ENABLED:
    INSTALLED_APPS += ["health_check.contrib.redis"]
    REDIS_PORT = str(config("REDIS_PORT", cast=int, default=6379))
    REDIS_ADDRESS = config("REDIS_ADDRESS")
    REDIS_DB = config("REDIS_DB", cast=int, default=0)
    if config("REDIS_SENTINEL_ENABLED", default=False, cast=bool):
        REDIS_SENTINEL_ADDRESS = config(
            "REDIS_SENTINEL_ADDRESS",
            cast=lambda v: [(i[0], int(i[1])) for i in [(s.strip().split(":")) for s in v.split(",")]],
        )
        DJANGO_REDIS_CONNECTION_FACTORY = "django_redis.pool.SentinelConnectionFactory"
        CACHES = {
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": [
                    f"redis://{REDIS_ADDRESS}:{REDIS_PORT}/{REDIS_DB}",
                ],
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.SentinelClient",
                    "PASSWORD": config("REDIS_PASSWORD", default=None),
                    "PARSER_CLASS": "redis.connection._HiredisParser",
                    "CONNECTION_POOL_CLASS": "redis.sentinel.SentinelConnectionPool",
                    "SENTINELS": REDIS_SENTINEL_ADDRESS,
                    "SENTINEL_KWARGS": {"password": config("REDIS_SENTINEL_PASSWORD", default=None)},
                    "CONNECTION_POOL_CLASS_KWARGS": {
                        "max_connections": 300,
                        "timeout": 20,
                    },
                    "MAX_CONNECTIONS": 2000,
                    "PICKLE_VERSION": -1,
                },
                "KEY_PREFIX": "backend",
            },
        }
        # healtcheck doesn't support redis sentinel
        if "health_check.contrib.redis" in INSTALLED_APPS:
            INSTALLED_APPS.remove("health_check.contrib.redis")
    else:
        CACHES = {
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": [
                    f"redis://{REDIS_ADDRESS}:{REDIS_PORT}/{REDIS_DB}",
                ],
                "OPTIONS": {
                    "DB": REDIS_DB,
                    "PASSWORD": config("REDIS_PASSWORD", default=None),
                    "PARSER_CLASS": "redis.connection._HiredisParser",
                    "CONNECTION_POOL_CLASS": "redis.BlockingConnectionPool",
                    "CONNECTION_POOL_CLASS_KWARGS": {
                        "max_connections": 100,
                        "timeout": 30,
                    },
                    "MAX_CONNECTIONS": 2000,
                    "PICKLE_VERSION": -1,  # Use the latest protocol version
                },
                "KEY_PREFIX": "backend",
            },
        }
        REDIS_URL = f"redis://{REDIS_ADDRESS}:{REDIS_PORT}"
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
            "LOCATION": config("CACHE_FILE_LOCATION", default="/tmp/django_cache"),
        }
    }
    # For running redis labs instances: https://app.redislabs.com/#/sign-up
