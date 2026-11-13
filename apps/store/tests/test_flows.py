from decimal import Decimal

import pytest
from django.core import mail
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone

from apps.catalog.models import Product
from apps.complaints.models import Complaint
from apps.customers.models import Consent
from apps.orders.models import Order, Payment
from apps.quotes.models import Quote

CHECKOUT = {
    "doc_type": "dni",
    "doc_number": "45678912",
    "full_name": "Ana Pérez",
    "email": "ana@example.com",
    "phone": "987654321",
    "receipt_type": "boleta",
    "delivery": "home",
    "department": "15",
    "lima_province": "01",
    "district": "Miraflores",
    "address": "Av. Larco 123",
    "accept_terms": "on",
}


@pytest.fixture
def demo(db):
    with override_settings(DEBUG=True):
        call_command("load_demo_data", stdout=open("/dev/null", "w"))  # noqa: SIM115


def add(client, sku, qty=1):
    product = Product.objects.get(sku=sku)
    return client.post(
        "/carrito/actualizar/", {"product": product.pk, "quantity": qty, "action": "add"}
    )


@pytest.mark.parametrize(
    "url",
    [
        "/",
        "/productos/",
        "/categoria/ticketeras/",
        "/producto/demo-tk80-usb/",
        "/productos/?q=ticketera&orden=precio-asc",
        "/carrito/",
        "/cotizar/",
        "/libro-de-reclamaciones/",
        "/terminos/",
        "/privacidad/",
        "/derechos-arco/",
        "/envios/",
    ],
)
def test_public_pages_render(client, demo, url):
    assert client.get(url).status_code == 200


def test_unknown_page_is_friendly_404(client, demo):
    assert client.get("/no-existe/").status_code == 404


def test_quote_only_product_cannot_enter_cart(client, demo):
    add(client, "DEMO-KIT-BOD")
    assert client.session.get("cart", {}) == {}


@override_settings(FAKE_PAYMENTS=True, DEBUG=True)
def test_full_purchase_flow(client, demo, django_capture_on_commit_callbacks):
    add(client, "DEMO-TK80-USB", 2)
    response = client.post("/checkout/", CHECKOUT)
    order = Order.objects.get()
    assert response.status_code == 302 and order.tracking_token in response["Location"]
    # Precio desde la BD + envío Lima Metropolitana (S/ 10)
    assert order.total_pen == Decimal("588.00")
    assert Consent.objects.filter(customer=order.customer).count() == 3
    assert client.session.get("cart") is None

    with django_capture_on_commit_callbacks(execute=True):
        paid = client.post(
            f"/pagar/{order.tracking_token}/cobrar/",
            data='{"token": "demo"}',
            content_type="application/json",
        )
    assert paid.json()["ok"] is True
    order.refresh_from_db()
    assert order.status == Order.Status.PAID and order.paid_at
    assert Payment.objects.get(order=order).status == Payment.Status.SUCCEEDED
    assert "AltoFact" in order.receipt_error  # pendiente de emisión manual
    subjects = [m.subject for m in mail.outbox]
    assert any("Recibimos tu pago" in s for s in subjects)
    assert any("Nuevo pedido pagado" in s for s in subjects)

    again = client.post(
        f"/pagar/{order.tracking_token}/cobrar/",
        data='{"token": "demo"}',
        content_type="application/json",
    )
    assert again.status_code == 402  # no se cobra dos veces
    assert client.get(f"/pedido/{order.tracking_token}/").status_code == 200


def test_factura_requires_ruc(client, demo):
    add(client, "DEMO-TK80-USB")
    response = client.post("/checkout/", {**CHECKOUT, "receipt_type": "factura"})
    assert response.status_code == 200 and not Order.objects.exists()


def test_checkout_requires_consent(client, demo):
    add(client, "DEMO-TK80-USB")
    data = {k: v for k, v in CHECKOUT.items() if k != "accept_terms"}
    client.post("/checkout/", data)
    assert not Order.objects.exists()


def test_real_payments_reject_missing_token(client, demo):
    add(client, "DEMO-TK80-USB")
    client.post("/checkout/", CHECKOUT)
    order = Order.objects.get()
    response = client.post(
        f"/pagar/{order.tracking_token}/cobrar/",
        data='{"token": "x"}',
        content_type="application/json",
    )
    assert response.status_code == 400


@override_settings(DEBUG=True)
def test_quote_request_and_payment_link(client, demo):
    response = client.post(
        "/cotizar/",
        {
            "business_type": "Restaurante o cafetería",
            "registers": 2,
            "detail": "Kit con KDS",
            "delivery_note": "Cusco",
            "doc_type": "ruc",
            "doc_number": "20123456789",
            "full_name": "Resto SAC",
            "email": "resto@example.com",
            "phone": "912345678",
            "accept_terms": "on",
        },
    )
    assert response.status_code == 302
    quote = Quote.objects.get()
    assert any("Nueva cotización" in m.subject for m in mail.outbox)
    assert client.get("/cotizar/enviada/").status_code == 200

    quote.proposed_total_pen = Decimal("4500.00")
    quote.issue_payment_link(72)
    quote.save()
    response = client.post(
        f"/cotizar/pagar/{quote.payment_token}/",
        {
            "receipt_type": "factura",
            "delivery": "agency",
            "department": "08",
            "district": "Cusco",
            "address": "Shalom Av. de la Cultura",
            "accept_terms": "on",
        },
    )
    order = Order.objects.get(quote=quote)
    assert response.status_code == 302
    assert order.total_pen == Decimal("4500.00") and order.shipping_zone.name == "Sierra"


def test_expired_quote_link(client, demo):
    quote = Quote.objects.create(
        customer=_customer(), business_type="Otro", detail="x", proposed_total_pen=Decimal("100")
    )
    quote.issue_payment_link(1)
    quote.payment_link_expires_at = timezone.now() - timezone.timedelta(minutes=1)
    quote.save()
    assert client.get(f"/cotizar/pagar/{quote.payment_token}/").status_code == 410


@override_settings(DEBUG=True)
def test_complaint_book(client, demo):
    response = client.post(
        "/libro-de-reclamaciones/",
        {
            "full_name": "Ana Pérez",
            "doc_type": "dni",
            "doc_number": "45678912",
            "consumer_address": "Av. Larco 123",
            "email": "ana@example.com",
            "phone": "987654321",
            "kind": "reclamo",
            "product_or_service": "Ticketera",
            "detail": "No imprime",
            "request": "Cambio del equipo",
            "accept": "on",
        },
    )
    assert response.status_code == 302
    complaint = Complaint.objects.get()
    assert complaint.number == 1
    assert any("Libro de Reclamaciones" in m.subject for m in mail.outbox)


def test_forms_reject_bots_without_debug(client, demo):
    response = client.post(
        "/derechos-arco/", {"email": "a@b.pe", "kind": "access", "detail": "Quiero mis datos"}
    )
    assert "robot" in response.content.decode()


def test_rate_limit_on_quote_form(client, demo):
    for _ in range(5):
        client.post("/cotizar/", {})
    assert client.post("/cotizar/", {}).status_code == 429


def _customer():
    from apps.customers.models import Customer

    return Customer.objects.create(
        doc_type="dni", doc_number="45678912", full_name="A", email="a@b.pe", phone="987654321"
    )
