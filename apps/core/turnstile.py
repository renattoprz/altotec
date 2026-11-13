"""Verificación de Cloudflare Turnstile (anti-bots) en el servidor."""

import logging

import requests
from django.conf import settings

log = logging.getLogger(__name__)
VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def enabled() -> bool:
    return bool(settings.TURNSTILE_SITE_KEY and settings.TURNSTILE_SECRET_KEY)


def verify(request) -> bool:
    """Devuelve True si el desafío es válido. Sin llaves configuradas solo pasa en DEBUG."""
    if not enabled():
        return settings.DEBUG
    token = request.POST.get("cf-turnstile-response", "")
    if not token:
        return False
    try:
        response = requests.post(
            VERIFY_URL,
            data={
                "secret": settings.TURNSTILE_SECRET_KEY,
                "response": token,
                "remoteip": client_ip(request),
            },
            timeout=(3, 10),
        )
        return bool(response.json().get("success"))
    except (requests.RequestException, ValueError):
        log.warning("No se pudo verificar Turnstile")
        return False


def client_ip(request) -> str:
    return request.META.get("HTTP_CF_CONNECTING_IP") or request.META.get("REMOTE_ADDR", "")
