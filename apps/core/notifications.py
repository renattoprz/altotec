"""Correos transaccionales. En local se imprimen en consola; en producción van por SMTP."""

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

log = logging.getLogger(__name__)


def send(template: str, context: dict, *, to: list[str], subject: str) -> None:
    body = render_to_string(f"emails/{template}.txt", context)
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, to, fail_silently=False)
    except Exception:  # noqa: BLE001 - un correo fallido no debe romper la venta
        log.exception("No se pudo enviar el correo %s", template)


def notify_admin(template: str, context: dict, *, subject: str) -> None:
    if settings.STORE_ADMIN_EMAILS:
        send(template, context, to=settings.STORE_ADMIN_EMAILS, subject=subject)
