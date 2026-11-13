"""Casos de uso de pedidos: crear, cobrar y procesar un pedido pagado."""

import logging
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.core import notifications
from apps.customers.models import Consent, Customer

from . import altofact, culqi
from .models import Order, OrderItem, Payment, ShippingZone
from .pricing import PricedCart

log = logging.getLogger(__name__)


class PaymentError(Exception):
    pass


def _find_or_create_customer(data: dict) -> Customer:
    """Reutiliza al cliente si el documento Y el correo coinciden.

    Privacidad: si alguien escribe el DNI de otra persona con un correo distinto,
    se crea un registro aparte y nunca se sobrescriben los datos de contacto del
    titular (evita que un tercero redirija avisos de pedidos ajenos). En una compra
    repetida del mismo titular se actualizan nombre, teléfono y preferencia de
    publicidad con lo último que indicó.
    """
    email = data["email"].strip()
    customer = (
        Customer.objects.filter(
            doc_type=data["doc_type"],
            doc_number=data["doc_number"],
            email__iexact=email,
        )
        .order_by("pk")
        .first()
    )
    fields = {
        "full_name": data["full_name"],
        "phone": data["phone"],
        "marketing_consent": data.get("marketing_consent", False),
    }
    if customer is None:
        return Customer.objects.create(
            doc_type=data["doc_type"], doc_number=data["doc_number"], email=email, **fields
        )
    for name, value in fields.items():
        setattr(customer, name, value)
    customer.save(update_fields=list(fields))
    return customer


def save_customer(data: dict, *, ip: str | None) -> Customer:
    customer = _find_or_create_customer(data)
    version = settings.POLICY_VERSION
    Consent.objects.bulk_create(
        [
            Consent(
                customer=customer,
                purpose=Consent.Purpose.TERMS,
                granted=True,
                policy_version=version,
                ip=ip,
            ),
            Consent(
                customer=customer,
                purpose=Consent.Purpose.PRIVACY,
                granted=True,
                policy_version=version,
                ip=ip,
            ),
            Consent(
                customer=customer,
                purpose=Consent.Purpose.MARKETING,
                granted=bool(data.get("marketing_consent")),
                policy_version=version,
                ip=ip,
            ),
        ]
    )
    return customer


@transaction.atomic
def create_order(cart: PricedCart, data: dict, *, ubigeo: str, ip: str | None) -> Order:
    customer = save_customer(data, ip=ip)
    order = Order.objects.create(
        customer=customer,
        receipt_type=data["receipt_type"],
        delivery=data["delivery"],
        address=data["address"],
        district=data.get("district", ""),
        reference=data.get("reference", ""),
        ubigeo=ubigeo,
        shipping_zone=cart.shipping_zone,
        subtotal_pen=cart.subtotal_pen,
        shipping_pen=cart.shipping_pen,
        total_pen=cart.total_pen,
    )
    OrderItem.objects.bulk_create(
        [
            OrderItem(
                order=order,
                product=line.product,
                quantity=line.quantity,
                unit_price_pen=line.unit_price_pen,
            )
            for line in cart.lines
        ]
    )
    return order


@transaction.atomic
def create_order_from_quote(quote, data: dict, *, ubigeo: str, zone: ShippingZone) -> Order:
    order = Order.objects.create(
        customer=quote.customer,
        quote=quote,
        receipt_type=data["receipt_type"],
        delivery=data["delivery"],
        address=data["address"],
        district=data.get("district", ""),
        reference=data.get("reference", ""),
        ubigeo=ubigeo,
        shipping_zone=zone,
        subtotal_pen=quote.proposed_total_pen,
        shipping_pen=Decimal("0"),  # el envío va incluido en el monto cotizado
        total_pen=quote.proposed_total_pen,
    )
    return order


def charge(order: Order, *, token: str) -> Payment:
    """Cobra con Culqi. El resultado lo decide la respuesta servidor a servidor de Culqi."""
    if order.status != Order.Status.PENDING_PAYMENT:
        raise PaymentError("Este pedido ya no está pendiente de pago.")
    if settings.FAKE_PAYMENTS:
        if not settings.DEBUG:  # defensa extra: nunca en producción
            raise PaymentError("Pagos simulados deshabilitados.")
        result = {
            "id": f"chr_demo_{order.code}",
            "amount": order.total_cents,
            "outcome": {"type": culqi.SUCCESS_OUTCOME},
        }
    else:
        try:
            result = culqi.create_charge(
                amount_cents=order.total_cents,
                email=order.customer.email,
                source_id=token,
                order_code=order.code,
            )
        except culqi.CulqiError as exc:
            raise PaymentError(str(exc)) from exc

    with transaction.atomic():
        payment, _ = Payment.objects.get_or_create(
            culqi_charge_id=result["id"],
            defaults={"order": order, "amount_cents": order.total_cents},
        )
        if culqi.charge_succeeded(result) and result.get("amount") == order.total_cents:
            payment.status = Payment.Status.SUCCEEDED
            payment.save()
            mark_paid(order)
        else:
            payment.status = Payment.Status.FAILED
            payment.save()
            raise PaymentError("El pago no fue aprobado.")
    return payment


def mark_paid(order: Order) -> None:
    order = Order.objects.select_for_update().get(pk=order.pk)
    if order.status != Order.Status.PENDING_PAYMENT:
        return  # idempotente
    order.status = Order.Status.PAID
    order.paid_at = timezone.now()
    order.save()
    transaction.on_commit(lambda: after_payment(order.pk))


def after_payment(order_id: int) -> None:
    order = Order.objects.select_related("customer").get(pk=order_id)
    try:
        order.receipt_number = altofact.emit_receipt(order)
        order.receipt_error = ""
    except altofact.AltoFactError as exc:
        order.receipt_error = str(exc)[:250]
    order.save()
    context = {
        "order": order,
        "items": order.items.select_related("product"),
        "tracking_url": f"{settings.SITE_URL}/pedido/{order.tracking_token}/",
    }
    notifications.send(
        "order_paid_customer",
        context,
        to=[order.customer.email],
        subject=f"Recibimos tu pago · Pedido {order.code}",
    )
    notifications.notify_admin(
        "order_paid_admin", context, subject=f"Nuevo pedido pagado {order.code}"
    )


def notify_shipped(order: Order) -> None:
    context = {
        "order": order,
        "tracking_url": f"{settings.SITE_URL}/pedido/{order.tracking_token}/",
    }
    notifications.send(
        "order_shipped",
        context,
        to=[order.customer.email],
        subject=f"Tu pedido {order.code} está en camino",
    )
