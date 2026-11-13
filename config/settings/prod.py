"""Producción: Cloud Run detrás de Cloudflare."""

from .base import *  # noqa: F403
from .base import env, env_list

DEBUG = False

# TLS de punta a punta; Cloudflare termina TLS y reenvía X-Forwarded-Proto.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
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
