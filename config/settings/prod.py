"""Producción: DigitalOcean detrás de Cloudflare."""

from .base import *  # noqa: F403
from .base import env, env_list

DEBUG = False

# TLS de punta a punta; Cloudflare termina TLS y reenvía X-Forwarded-Proto.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
# El chequeo de salud del balanceador llega por HTTP interno.
SECURE_REDIRECT_EXEMPT = [r"^healthz$"]
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", "https://tec.codaltoperu.com")

# HSTS: 1 año, incluye subdominios de codaltoperu.com (decisión de dominio único).
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Axes: IP real del cliente detrás de Cloudflare.
AXES_IPWARE_META_PRECEDENCE_ORDER = ["HTTP_CF_CONNECTING_IP", "REMOTE_ADDR"]

MEDIA_ORIGIN = env("MEDIA_ORIGIN")

# Garantía: el pago simulado jamás se activa en producción.
FAKE_PAYMENTS = False

# Solo para la prueba de humo local con docker compose (sin TLS). Nunca en producción.
if env("DJANGO_INSECURE_LOCAL_HTTP") == "1" and set(ALLOWED_HOSTS) <= {"localhost", "127.0.0.1"}:  # noqa: F405
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_NAME = "altotec_session"
    CSRF_COOKIE_NAME = "altotec_csrf"
    SECURE_HSTS_SECONDS = 0
