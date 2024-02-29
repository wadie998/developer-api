import sys

from settings.configs.env import ENV

if ENV:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "health_check": {"()": "settings.logging.custom_gunicorn_logger.HealthCheckFilter"},
        },
        "formatters": {
            "verbose": {"format": "%(levelname)s File %(pathname)s, line %(lineno)d, %(message)s"},
        },
        "handlers": {
            "console": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "verbose",
                "stream": sys.stdout,
            },
            "mail_admins": {
                "level": "ERROR",
                "class": "settings.logging.custom_admin_email_handler.CustomAdminEmailHandler",
                "include_html": False,
                "filters": ["health_check"],
            },
            "critical_mail": {
                "level": "CRITICAL",
                "class": "settings.logging.custom_admin_email_handler.CustomAdminEmailHandler",
                "include_html": False,
            },
        },
        "loggers": {
            "": {
                "handlers": ["console", "critical_mail"],
                "level": "INFO",
                "propagate": True,
            },
            "django.request": {
                "handlers": ["mail_admins"],
                "level": "ERROR",
                "propagate": True,
            },
        },
    }
else:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {"format": "%(levelname)s File %(pathname)s, line %(lineno)d, %(message)s"},
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
            "mail_admins": {
                "level": "ERROR",
                "class": "settings.logging.custom_admin_email_handler.CustomAdminEmailHandler",
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": True,
            },
            "django.request": {
                "handlers": ["mail_admins"],
                "level": "ERROR",
                "propagate": False,
            },
        },
    }
