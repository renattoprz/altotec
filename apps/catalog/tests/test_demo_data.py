import pytest
from django.core.management import CommandError, call_command
from django.test import override_settings

from apps.catalog.models import Product
from apps.orders.models import ShippingZone
from apps.orders.pricing import price_cart


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_demo_data_loads_and_is_idempotent():
    call_command("load_demo_data")
    call_command("load_demo_data")
    assert Product.objects.count() == 15
    assert all("DEMO" in p.name for p in Product.objects.all())
    assert ShippingZone.objects.count() == 5
    ticketera = Product.objects.get(sku="DEMO-TK80-USB")
    assert price_cart({ticketera.pk: 1}, ubigeo="080101").shipping_zone.name == "Sierra"


@pytest.mark.django_db
def test_demo_data_refuses_outside_debug():
    with pytest.raises(CommandError):
        call_command("load_demo_data")
