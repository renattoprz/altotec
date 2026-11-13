from django.conf import settings

from apps.catalog.models import Category

from . import turnstile


def store(request):
    cart = request.session.get("cart", {})
    return {
        "cart_count": sum(cart.values()) if isinstance(cart, dict) else 0,
        "store_whatsapp": settings.STORE_WHATSAPP,
        "turnstile_site_key": settings.TURNSTILE_SITE_KEY if turnstile.enabled() else "",
        "demo_mode": settings.DEBUG,
        "nav_categories": Category.objects.filter(products__published=True).distinct(),
    }
