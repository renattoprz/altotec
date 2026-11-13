"""Desarrollo local. Nunca usar en producción."""

from pathlib import Path

from config.envfile import load as _load_env

_load_env(Path(__file__).resolve().parent.parent.parent / ".env")

from .base import *  # noqa: E402, F403
from .base import BASE_DIR, env  # noqa: E402

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Los prefijos __Host- exigen HTTPS; en local usamos nombres simples.
SESSION_COOKIE_NAME = "altotec_session"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
SITE_URL = "http://localhost:8000"
STORE_ADMIN_EMAILS = ["admin@localhost"]
STORE_WHATSAPP = env("STORE_WHATSAPP", "51999999999")
FAKE_PAYMENTS = not env("CULQI_SECRET_KEY")
CSRF_COOKIE_NAME = "altotec_csrf"

if env("DB_HOST"):
    pass  # usa PostgreSQL de base.py
else:
    DATABASES = {
        "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}
    }
