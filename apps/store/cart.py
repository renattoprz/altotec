"""Carrito en la sesión del navegador (sin cuenta). Solo guarda ids y cantidades."""

from decimal import Decimal

from apps.catalog.models import Product
from apps.orders.pricing import MAX_QTY_PER_ITEM

SESSION_KEY = "cart"
MAX_LINES = 30


def get(request) -> dict[int, int]:
    raw = request.session.get(SESSION_KEY, {})
    cart = {}
    if isinstance(raw, dict):
        for key, qty in raw.items():
            if str(key).isdigit() and isinstance(qty, int) and 0 < qty <= MAX_QTY_PER_ITEM:
                cart[int(key)] = qty
    return cart


def save(request, cart: dict[int, int]) -> None:
    request.session[SESSION_KEY] = {str(k): v for k, v in cart.items()}


def set_quantity(request, product_id: int, qty: int) -> None:
    cart = get(request)
    if qty <= 0:
        cart.pop(product_id, None)
    elif product_id in cart or len(cart) < MAX_LINES:
        cart[product_id] = min(qty, MAX_QTY_PER_ITEM)
    save(request, cart)


def clear(request) -> None:
    request.session.pop(SESSION_KEY, None)


def lines(request):
    cart = get(request)
    products = Product.objects.filter(pk__in=cart, published=True).select_related("category")
    result, subtotal = [], Decimal("0")
    for product in products:
        qty = cart[product.pk]
        total = product.price_pen * qty
        subtotal += total
        result.append(
            {
                "product": product,
                "quantity": qty,
                "total": total,
                "available": product.can_buy_online,
            }
        )
    return result, subtotal
