import os

from decouple import config

ENV = os.environ.get("ENV", None)

ELASTIC_APM_CONFIG = {
    "SERVICE_NAME": config("ELASTIC_APM_SERVICE_NAME", default="django-template-app"),
    "SECRET_TOKEN": config("ELASTIC_APM_SECRET_TOKEN", default=None),
    "API_KEY": config("ELASTIC_APM_API_KEY", default=None),
    "SERVER_URL": config("ELASTIC_APM_ADDRESS"),
    "ENVIRONMENT": ENV,
    # show url instead of views
    "DJANGO_TRANSACTION_NAME_FROM_ROUTE": True,
    "TRANSACTIONS_IGNORE_PATTERNS": ["GET api/ht/?"],
    "ENABLED": config("ELASTIC_APM_ENABLED", default=True, cast=bool),
    "METRICS_INTERVAL": config("ELASTIC_APM_METRICS_INTERVAL", default="2m"),
    "DISABLE_METRICS": config("ELASTIC_APM_DISABLE_METRICS", default=None),
    "CENTRAL_CONFIG": config("ELASTIC_APM_CENTRAL_CONFIG", default=False, cast=bool),
}
