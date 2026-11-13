import json
import logging

from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from apps.catalog.models import Category, Product
from apps.core.ratelimit import ratelimit
from apps.core.turnstile import client_ip
from apps.core.ubigeo import describe
from apps.orders import services
from apps.orders.models import Order, ShippingZone
from apps.orders.pricing import CartError, price_cart

from . import cart as cart_store
from .forms import CheckoutForm

log = logging.getLogger(__name__)
PAGE_SIZE = 12
SORTS = {
    "relevancia": ("category__order", "name"),
    "precio-asc": ("price_pen",),
    "precio-desc": ("-price_pen",),
    "nombre": ("name",),
}


def _published():
    return (
        Product.objects.filter(published=True).select_related("category").prefetch_related("images")
    )


@require_GET
def home(request):
    categories = Category.objects.filter(products__published=True).distinct()
    featured = _published().filter(sale_mode=Product.SaleMode.ONLINE)[:8]
    kits = _published().filter(category__slug="kits-pos")[:3]
    zones = ShippingZone.objects.filter(active=True).order_by("price_pen")
    return render(
        request,
        "store/home.html",
        {
            "categories": categories,
            "featured": featured,
            "kits": kits,
            "zones": zones,
        },
    )


@require_GET
def catalog(request, slug=None):
    products = _published()
    category = None
    if slug:
        category = get_object_or_404(Category, slug=slug)
        products = products.filter(category=category)
    query = request.GET.get("q", "").strip()[:80]
    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(brand__icontains=query)
            | Q(sku__icontains=query)
            | Q(category__name__icontains=query)
        )
    mode = request.GET.get("modo")
    if mode in Product.SaleMode.values:
        products = products.filter(sale_mode=mode)
    try:
        price_max = int(request.GET.get("max", "") or 0)
    except ValueError:
        price_max = 0
    if price_max > 0:
        products = products.filter(price_pen__lte=price_max)
    sort = request.GET.get("orden", "relevancia")
    products = products.order_by(*SORTS.get(sort, SORTS["relevancia"]))
    page = Paginator(products, PAGE_SIZE).get_page(request.GET.get("pagina"))
    params = request.GET.copy()
    params.pop("pagina", None)
    return render(
        request,
        "store/catalog.html",
        {
            "category": category,
            "categories": Category.objects.all(),
            "page": page,
            "query": query,
            "mode": mode,
            "price_max": price_max or "",
            "sort": sort,
            "sorts": [
                ("relevancia", "Relevancia"),
                ("precio-asc", "Menor precio"),
                ("precio-desc", "Mayor precio"),
                ("nombre", "Nombre"),
            ],
            "querystring": params.urlencode(),
        },
    )


@require_GET
def product_detail(request, slug):
    product = get_object_or_404(_published(), slug=slug)
    related = _published().filter(category=product.category).exclude(pk=product.pk)[:4]
    return render(request, "store/product.html", {"product": product, "related": related})


@require_POST
@ratelimit("cart", limit=60, window_seconds=60)
def cart_update(request):
    try:
        product_id = int(request.POST.get("product", ""))
        qty = int(request.POST.get("quantity", "1"))
    except ValueError:
        return redirect("store:cart")
    product = Product.objects.filter(pk=product_id, published=True).first()
    if product is None or not product.can_buy_online:
        messages.error(request, "Ese producto se vende bajo cotización.")
        return redirect("store:cart")
    if request.POST.get("action") == "add":
        qty = cart_store.get(request).get(product_id, 0) + qty
        messages.success(request, f"Agregaste {product.name} al carrito.")
    cart_store.set_quantity(request, product_id, qty)
    return redirect("store:cart")


@require_GET
def cart_view(request):
    lines, subtotal = cart_store.lines(request)
    return render(
        request,
        "store/cart.html",
        {
            "lines": lines,
            "subtotal": subtotal,
            "zones": ShippingZone.objects.filter(active=True).order_by("price_pen"),
        },
    )


@ratelimit("checkout", limit=10, window_seconds=600)
def checkout(request):
    lines, subtotal = cart_store.lines(request)
    if not lines:
        return redirect("store:cart")
    form = CheckoutForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        try:
            priced = price_cart(cart_store.get(request), data["ubigeo"])
        except CartError as exc:
            messages.error(request, str(exc))
        else:
            order = services.create_order(
                priced, data, ubigeo=data["ubigeo"], ip=client_ip(request)
            )
            cart_store.clear(request)
            return redirect("store:pay", token=order.tracking_token)
    return render(
        request,
        "store/checkout.html",
        {
            "form": form,
            "lines": lines,
            "subtotal": subtotal,
            "zones": ShippingZone.objects.filter(active=True).order_by("price_pen"),
        },
    )


def _pending_order(token):
    order = (
        Order.objects.select_related("customer", "shipping_zone")
        .filter(tracking_token=token)
        .first()
    )
    if order is None:
        raise Http404
    return order


@require_GET
def pay(request, token):
    order = _pending_order(token)
    if order.status != Order.Status.PENDING_PAYMENT:
        return redirect("store:tracking", token=token)
    return render(
        request,
        "store/pay.html",
        {
            "order": order,
            "items": order.items.select_related("product"),
            "culqi_public_key": settings.CULQI_PUBLIC_KEY,
            "fake_payments": settings.FAKE_PAYMENTS,
            "place": describe(order.ubigeo),
        },
    )


@require_POST
@ratelimit("charge", limit=8, window_seconds=600)
def charge(request, token):
    order = _pending_order(token)
    try:
        payload = json.loads(request.body or b"{}")
    except ValueError:
        payload = {}
    culqi_token = str(payload.get("token", ""))[:64]
    if not settings.FAKE_PAYMENTS and not culqi_token.startswith(("tkn_", "ype_")):
        return JsonResponse({"ok": False, "message": "Token de pago inválido."}, status=400)
    try:
        services.charge(order, token=culqi_token)
    except services.PaymentError as exc:
        return JsonResponse({"ok": False, "message": str(exc)}, status=402)
    return JsonResponse({"ok": True, "redirect": f"/pedido/{order.tracking_token}/?nuevo=1"})


@require_GET
def tracking(request, token):
    order = get_object_or_404(Order.objects.select_related("shipping_zone"), tracking_token=token)
    steps = [
        Order.Status.PAID,
        Order.Status.PREPARING,
        Order.Status.SHIPPED,
        Order.Status.DELIVERED,
    ]
    reached = steps.index(order.status) if order.status in steps else -1
    return render(
        request,
        "store/tracking.html",
        {
            "order": order,
            "items": order.items.select_related("product"),
            "steps": [(s.label, i <= reached) for i, s in enumerate(steps)],
            "just_paid": request.GET.get("nuevo") == "1",
            "place": describe(order.ubigeo),
        },
    )


def page(request, template):
    return render(request, f"legal/{template}.html")
