from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SQLITE3_CONFIG = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
