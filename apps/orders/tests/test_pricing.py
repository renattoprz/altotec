from decimal import Decimal

import pytest

from apps.catalog.models import Product
from apps.catalog.tests.factories import make_product, make_zone
from apps.orders.pricing import CartError, price_cart


@pytest.mark.django_db
def test_totals_come_from_database_not_from_browser():
    product = make_product(price="499.00")
    make_zone(price="15.00", departments=["15"])
    cart = price_cart({product.pk: 2}, ubigeo="150101")
    assert cart.subtotal_pen == Decimal("998.00")
    assert cart.total_pen == Decimal("1013.00")
    assert cart.total_cents == 101300


@pytest.mark.django_db
@pytest.mark.parametrize("qty", [0, -1, 51, "2"])
def test_invalid_quantities_are_rejected(qty):
    product = make_product()
    make_zone()
    with pytest.raises(CartError):
        price_cart({product.pk: qty}, ubigeo="150101")


@pytest.mark.django_db
def test_quote_only_products_cannot_be_checked_out():
    product = make_product(mode=Product.SaleMode.QUOTE)
    make_zone()
    with pytest.raises(CartError):
        price_cart({product.pk: 1}, ubigeo="150101")


@pytest.mark.django_db
def test_unknown_shipping_destination_is_rejected():
    product = make_product()
    make_zone(departments=["15"])
    with pytest.raises(CartError):
        price_cart({product.pk: 1}, ubigeo="080101")


@pytest.mark.django_db
def test_province_zone_wins_over_department_zone():
    product = make_product()
    metro = make_zone(price="10.00", departments=["1501", "07"])
    make_zone(price="20.00", departments=["15"])
    assert price_cart({product.pk: 1}, ubigeo="150101").shipping_zone == metro
    assert price_cart({product.pk: 1}, ubigeo="150501").shipping_pen == Decimal("20.00")
