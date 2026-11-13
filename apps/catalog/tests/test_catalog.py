from datetime import timedelta

import pytest
from django.utils import timezone

from apps.audit.models import AuditLog
from apps.catalog.models import Product

from .factories import make_product


@pytest.mark.django_db
def test_online_product_with_fresh_stock_is_buyable():
    assert make_product().can_buy_online


@pytest.mark.django_db
def test_stale_stock_confirmation_blocks_online_sale():
    product = make_product(confirmed_at=timezone.now() - timedelta(days=3))
    assert not product.can_buy_online


@pytest.mark.django_db
def test_quote_products_are_never_buyable_online():
    assert not make_product(mode=Product.SaleMode.QUOTE).can_buy_online


@pytest.mark.django_db
def test_price_change_is_audited():
    product = make_product()
    product.price_pen = 450
    product.save()
    entry = AuditLog.objects.filter(action="modificar", entity="catalog.Product").get()
    assert entry.changes["price_pen"] == ["499.00", "450"]
