from .base import *

SECRET_KEY = "django-insecure-m-y_v14^)085=e=(v$)fl1ep$15q=!y3iy_0hh%69kqp@sgh+!"

DEBUG = True

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
