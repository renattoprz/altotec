"""Adaptador para emitir boleta o factura con AltoFact.

La API de AltoFact aún se está definiendo. Mientras no haya ALTOFACT_API_BASE
configurada, el comprobante queda pendiente y el panel lo muestra para emitirlo
manualmente. Cuando la API exista, solo se completa `_payload` y la llamada.
"""

import logging

import requests
from django.conf import settings

log = logging.getLogger(__name__)


class AltoFactError(Exception):
    pass


def enabled() -> bool:
    return bool(settings.ALTOFACT_API_BASE and settings.ALTOFACT_API_TOKEN)


def _payload(order) -> dict:
    customer = order.customer
    lines = [
        {
            "descripcion": item.product.name,
            "cantidad": item.quantity,
            "precio_unitario": str(item.unit_price_pen),
        }
        for item in order.items.select_related("product")
    ]
    if order.quote_id:
        lines.append(
            {
                "descripcion": f"Cotización {order.quote_id}",
                "cantidad": 1,
                "precio_unitario": str(order.subtotal_pen),
            }
        )
    if order.shipping_pen:
        lines.append(
            {
                "descripcion": "Servicio de envío",
                "cantidad": 1,
                "precio_unitario": str(order.shipping_pen),
            }
        )
    return {
        "tipo": order.receipt_type,
        "cliente": {
            "tipo_documento": customer.doc_type,
            "numero_documento": customer.doc_number,
            "nombre": customer.full_name,
            "correo": customer.email,
        },
        "moneda": "PEN",
        "items": lines,
        "referencia": order.code,
    }


def emit_receipt(order) -> str:
    """Emite el comprobante y devuelve su número (serie-correlativo)."""
    if not enabled():
        raise AltoFactError("AltoFact no está configurado: emitir manualmente.")
    try:
        response = requests.post(
            f"{settings.ALTOFACT_API_BASE}/comprobantes",
            json=_payload(order),
            headers={"Authorization": f"Bearer {settings.ALTOFACT_API_TOKEN}"},
            timeout=(5, 30),
        )
        response.raise_for_status()
        return response.json()["numero"]
    except (requests.RequestException, KeyError, ValueError) as exc:
        raise AltoFactError("No se pudo emitir el comprobante en AltoFact.") from exc
