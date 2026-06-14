from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = [
    host.strip() for host in os.getenv("ALLOWED_HOSTS", "").split(",") if host.strip()
]

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

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
