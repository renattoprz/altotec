"""Webhook de Culqi.

Defensa en profundidad:
1. Token secreto en la URL configurada en Culqi (comparación en tiempo constante).
2. El contenido del webhook NO se cree: se vuelve a consultar el cargo en la API
   de Culqi con la llave secreta y solo eso decide si el pedido está pagado.
3. Idempotente: procesar el mismo evento dos veces no cambia nada.
4. El monto cobrado debe coincidir exactamente con el registrado.
"""

import hmac
import json
import logging

from django.conf import settings
from django.db import transaction
from django.http import HttpResponse, HttpResponseForbidden
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import culqi, services
from .models import Payment

log = logging.getLogger(__name__)


def _extract_charge_id(payload: dict) -> str | None:
    data = payload.get("data")
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except ValueError:
            return None
    if isinstance(data, dict) and str(data.get("id", "")).startswith("chr_"):
        return data["id"]
    return None


@csrf_exempt  # Llamado servidor a servidor; protegido por token + verificación en la API.
@require_POST
def culqi_webhook(request, token: str):
    expected = settings.CULQI_WEBHOOK_TOKEN
    if not expected or not hmac.compare_digest(token, expected):
        return HttpResponseForbidden()
    try:
        payload = json.loads(request.body)
    except ValueError:
        return HttpResponse(status=400)

    charge_id = _extract_charge_id(payload)
    if charge_id is None:
        return HttpResponse(status=202)  # evento que no nos interesa

    try:
        charge = culqi.get_charge(charge_id)
    except culqi.CulqiError:
        log.warning("No se pudo verificar el cargo %s", charge_id)
        return HttpResponse(status=503)  # Culqi reintentará

    with transaction.atomic():
        payment = (
            Payment.objects.select_for_update()
            .select_related("order")
            .filter(culqi_charge_id=charge_id)
            .first()
        )
        if payment is None:
            log.warning("Webhook para cargo desconocido %s", charge_id)
            return HttpResponse(status=202)
        if payment.status == Payment.Status.SUCCEEDED:
            return HttpResponse(status=200)  # idempotente

        if culqi.charge_succeeded(charge) and charge.get("amount") == payment.amount_cents:
            payment.status = Payment.Status.SUCCEEDED
            payment.webhook_received_at = timezone.now()
            payment.save()
            services.mark_paid(payment.order)
        else:
            payment.status = Payment.Status.FAILED
            payment.webhook_received_at = timezone.now()
            payment.save()
    return HttpResponse(status=200)
