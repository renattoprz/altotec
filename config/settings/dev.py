"""Desarrollo local. Nunca usar en producción."""

from .base import *  # noqa: F403
from .base import BASE_DIR, env

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Los prefijos __Host- exigen HTTPS; en local usamos nombres simples.
SESSION_COOKIE_NAME = "altotec_session"
CSRF_COOKIE_NAME = "altotec_csrf"

if env("DB_HOST"):
    pass  # usa PostgreSQL de base.py
else:
    DATABASES = {
        "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}
    }
