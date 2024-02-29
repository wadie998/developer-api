from settings.configs.env import BASE_DIR

SQLITE3_CONFIG = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
