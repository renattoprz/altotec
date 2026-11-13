from urllib.parse import quote as urlquote

from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render

from apps.catalog.models import Product
from apps.core import notifications, turnstile
from apps.core.ratelimit import ratelimit
from apps.orders import services
from apps.orders.pricing import CartError, zone_for_ubigeo
from apps.store.forms import QuotePaymentForm

from .forms import QuoteRequestForm
from .models import Quote


@ratelimit("quote", limit=5, window_seconds=3600)
def request_quote(request):
    product = None
    sku = request.GET.get("producto", "")[:40]
    if sku:
        product = Product.objects.filter(sku=sku, published=True).first()
    initial = {"detail": f"Me interesa: {product.name}"} if product else {}
    form = QuoteRequestForm(request.POST if request.method == "POST" else None, initial=initial)
    if request.method == "POST":
        valid = form.is_valid()
        if not turnstile.verify(request):
            form.add_error(None, "No pudimos verificar que no eres un robot. Intenta de nuevo.")
        elif valid:
            data = form.cleaned_data
            customer = services.save_customer(data, ip=turnstile.client_ip(request))
            quote = Quote.objects.create(
                customer=customer,
                business_type=data["business_type"],
                registers=data["registers"],
                detail=data["detail"],
                delivery_note=data["delivery_note"],
            )
            notifications.notify_admin(
                "quote_new_admin", {"quote": quote}, subject=f"Nueva cotización #{quote.pk}"
            )
            request.session["last_quote"] = quote.pk
            return redirect("quotes:sent")
    return render(request, "quotes/request.html", {"form": form, "product": product})


def quote_sent(request):
    quote = Quote.objects.filter(pk=request.session.get("last_quote")).first()
    if quote is None:
        return redirect("quotes:request")
    text = (
        f"Hola AltoTec, acabo de pedir la cotización #{quote.pk} para mi "
        f"{quote.business_type.lower()} ({quote.registers} caja(s))."
    )
    whatsapp_url = f"https://wa.me/{settings.STORE_WHATSAPP}?text={urlquote(text)}"
    return render(request, "quotes/sent.html", {"quote": quote, "whatsapp_url": whatsapp_url})


@ratelimit("quote-pay", limit=10, window_seconds=600)
def pay_quote(request, token):
    quote = Quote.objects.select_related("customer").filter(payment_token=token).first()
    if quote is None:
        raise Http404
    existing = getattr(quote, "order", None)
    if existing is not None:
        return redirect("store:pay", token=existing.tracking_token)
    if not quote.payment_link_valid:
        return render(request, "quotes/expired.html", {"quote": quote}, status=410)
    form = QuotePaymentForm(request.POST if request.method == "POST" else None, quote=quote)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        try:
            zone = zone_for_ubigeo(data["ubigeo"])
        except CartError as exc:
            messages.error(request, str(exc))
        else:
            order = services.create_order_from_quote(quote, data, ubigeo=data["ubigeo"], zone=zone)
            return redirect("store:pay", token=order.tracking_token)
    return render(request, "quotes/pay.html", {"quote": quote, "form": form})
