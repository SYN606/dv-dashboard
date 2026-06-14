from .base import *
import os

DB_MODE = os.getenv("DB_MODE")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = [host.strip() for host in os.getenv("ALLOWED_HOSTS", "*").split(",")]



if DB_MODE == "postgres":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME", "your_db_name"),
            "USER": os.getenv("DB_USER", "your_db_user"),
            "PASSWORD": os.getenv("DB_PASSWORD", "your_db_password"),
            "HOST": os.getenv(
                "DB_HOST",
            ),
            "PORT": os.getenv("DB_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
