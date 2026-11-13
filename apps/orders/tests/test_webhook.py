from decimal import Decimal
from unittest import mock

import pytest

from apps.catalog.tests.factories import make_zone
from apps.customers.models import Customer
from apps.orders.culqi import CulqiError
from apps.orders.models import Order, Payment

URL = "/webhooks/culqi/test-webhook-token/"


@pytest.fixture
def payment(db):
    customer = Customer.objects.create(
        doc_type="dni", doc_number="45678912", full_name="Ana", email="a@b.pe", phone="999999999"
    )
    order = Order.objects.create(
        customer=customer,
        receipt_type="boleta",
        delivery="home",
        address="Av. 1",
        ubigeo="150101",
        shipping_zone=make_zone(),
        total_pen=Decimal("100.00"),
    )
    return Payment.objects.create(order=order, culqi_charge_id="chr_test_1", amount_cents=10000)


def _post(client, token="test-webhook-token"):
    return client.post(
        f"/webhooks/culqi/{token}/",
        data={"object": "event", "data": '{"id": "chr_test_1"}'},
        content_type="application/json",
    )


def test_wrong_token_is_forbidden(client, payment):
    assert _post(client, token="malo").status_code == 403


def test_successful_charge_marks_order_paid(client, payment):
    charge = {"id": "chr_test_1", "amount": 10000, "outcome": {"type": "venta_exitosa"}}
    with mock.patch("apps.orders.culqi.get_charge", return_value=charge):
        assert _post(client).status_code == 200
        assert _post(client).status_code == 200  # idempotente
    payment.refresh_from_db()
    assert payment.status == Payment.Status.SUCCEEDED
    assert payment.order.status == Order.Status.PAID


def test_amount_mismatch_does_not_mark_paid(client, payment):
    charge = {"id": "chr_test_1", "amount": 100, "outcome": {"type": "venta_exitosa"}}
    with mock.patch("apps.orders.culqi.get_charge", return_value=charge):
        _post(client)
    payment.refresh_from_db()
    assert payment.status == Payment.Status.FAILED
    assert payment.order.status == Order.Status.PENDING_PAYMENT


def test_webhook_payload_alone_is_never_trusted(client, payment):
    with mock.patch(
        "apps.orders.culqi.get_charge",
        side_effect=CulqiError,
    ):
        assert _post(client).status_code == 503
    payment.refresh_from_db()
    assert payment.order.status == Order.Status.PENDING_PAYMENT
