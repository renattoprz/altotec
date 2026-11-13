from decimal import Decimal

from django.utils import timezone

from apps.catalog.models import Category, Product, Supplier, SupplierOffer
from apps.orders.models import ShippingZone


def make_product(
    *, sku="TK-80", price="499.00", mode=Product.SaleMode.ONLINE, stock=True, confirmed_at=None
):
    category, _ = Category.objects.get_or_create(name="Ticketeras", slug="ticketeras")
    supplier, _ = Supplier.objects.get_or_create(
        ruc="20123456789", defaults={"business_name": "Prov SAC"}
    )
    product = Product.objects.create(
        sku=sku,
        name=f"Ticketera {sku}",
        slug=sku.lower(),
        category=category,
        price_pen=Decimal(price),
        sale_mode=mode,
        published=True,
    )
    SupplierOffer.objects.create(
        product=product,
        supplier=supplier,
        cost_pen=Decimal("300"),
        stock_confirmed=stock,
        confirmed_at=confirmed_at or (timezone.now() if stock else None),
    )
    return product


def make_zone(price="15.00", departments=("15",)):
    return ShippingZone.objects.create(
        name=f"Zona {price}",
        departments=list(departments),
        price_pen=Decimal(price),
        lead_time_days=2,
    )
