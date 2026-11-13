"""Cliente mínimo de la API de Culqi.

La tarjeta se tokeniza en el navegador con Culqi Checkout; aquí solo viaja el
token (source_id). La llave secreta vive únicamente en el servidor.
"""

import requests
from django.conf import settings

TIMEOUT = (5, 20)
SUCCESS_OUTCOME = "venta_exitosa"


class CulqiError(Exception):
    pass


def _headers() -> dict:
    if not settings.CULQI_SECRET_KEY:
        raise CulqiError("CULQI_SECRET_KEY no configurada.")
    return {
        "Authorization": f"Bearer {settings.CULQI_SECRET_KEY}",
        "Content-Type": "application/json",
    }


def create_charge(*, amount_cents: int, email: str, source_id: str, order_code: str) -> dict:
    response = requests.post(
        f"{settings.CULQI_API_BASE}/charges",
        json={
            "amount": amount_cents,
            "currency_code": "PEN",
            "email": email,
            "source_id": source_id,
            "metadata": {"order_code": order_code},
        },
        headers=_headers(),
        timeout=TIMEOUT,
    )
    data = response.json()
    if response.status_code >= 400:
        raise CulqiError(data.get("user_message") or "El cobro fue rechazado.")
    return data


def get_charge(charge_id: str) -> dict:
    response = requests.get(
        f"{settings.CULQI_API_BASE}/charges/{charge_id}", headers=_headers(), timeout=TIMEOUT
    )
    if response.status_code >= 400:
        raise CulqiError("No se pudo consultar el cargo.")
    return response.json()


def charge_succeeded(charge: dict) -> bool:
    return (charge.get("outcome") or {}).get("type") == SUCCESS_OUTCOME
