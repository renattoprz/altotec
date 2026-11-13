"""Pruebas automatizadas."""

import os

os.environ.setdefault("DJANGO_SECRET_KEY", "test-only-secret-key-not-for-production")

from .base import *  # noqa: E402, F403
from .base import BASE_DIR  # noqa: E402

DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost"]
SESSION_COOKIE_NAME = "altotec_session"
CSRF_COOKIE_NAME = "altotec_csrf"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "test.sqlite3"}}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]  # solo para pruebas rápidas
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
CULQI_SECRET_KEY = "sk_test_dummy"
CULQI_WEBHOOK_TOKEN = "test-webhook-token"
TURNSTILE_SECRET_KEY = "1x0000000000000000000000000000000AA"

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
STORE_ADMIN_EMAILS = ["admin@test.pe"]
STORE_WHATSAPP = "51999999999"
SITE_URL = "http://testserver"
