"""Cálculo de precios SIEMPRE en el servidor: nunca se confía en montos del navegador."""

from dataclasses import dataclass
from decimal import Decimal

from apps.catalog.models import Product

from .models import ShippingZone

MAX_QTY_PER_ITEM = 50


class CartError(ValueError):
    pass


@dataclass(frozen=True)
class PricedLine:
    product: Product
    quantity: int
    unit_price_pen: Decimal

    @property
    def total(self) -> Decimal:
        return self.unit_price_pen * self.quantity


@dataclass(frozen=True)
class PricedCart:
    lines: list[PricedLine]
    shipping_zone: ShippingZone
    subtotal_pen: Decimal
    shipping_pen: Decimal
    total_pen: Decimal

    @property
    def total_cents(self) -> int:
        return int((self.total_pen * 100).to_integral_value())


def zone_for_ubigeo(ubigeo: str) -> ShippingZone:
    department = ubigeo[:2]
    for zone in ShippingZone.objects.filter(active=True):
        if department in zone.departments:
            return zone
    raise CartError("No hacemos envíos a esa ubicación todavía.")


def price_cart(items: dict[int, int], ubigeo: str) -> PricedCart:
    """items: {product_id: cantidad} tal como llega del navegador (no confiable)."""
    if not items:
        raise CartError("El carrito está vacío.")
    products = {p.pk: p for p in Product.objects.filter(pk__in=items.keys(), published=True)}
    lines = []
    for product_id, qty in items.items():
        product = products.get(product_id)
        if product is None:
            raise CartError("Un producto ya no está disponible.")
        if not isinstance(qty, int) or not 1 <= qty <= MAX_QTY_PER_ITEM:
            raise CartError("Cantidad inválida.")
        if not product.can_buy_online:
            raise CartError(f"{product.name} se vende bajo cotización.")
        lines.append(PricedLine(product, qty, product.price_pen))
    zone = zone_for_ubigeo(ubigeo)
    subtotal = sum((line.total for line in lines), Decimal("0"))
    return PricedCart(lines, zone, subtotal, zone.price_pen, subtotal + zone.price_pen)
