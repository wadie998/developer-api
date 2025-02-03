import os
from pathlib import Path

from decouple import AutoConfig, config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

ENV = os.environ.get("ENV", None)

if ENV:
    config = AutoConfig("/run/secrets")  # noqa: F811
else:
    config = config
