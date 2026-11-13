from django.conf import settings
from django.contrib import admin, messages

from apps.core import notifications

from .models import Quote


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "business_type",
        "registers",
        "status",
        "proposed_total_pen",
        "payment_link_expires_at",
        "created_at",
    )
    list_filter = ("status", "business_type")
    readonly_fields = (
        "customer",
        "business_type",
        "registers",
        "detail",
        "delivery_note",
        "payment_link_expires_at",
        "created_at",
    )
    fields = (
        "customer",
        ("business_type", "registers"),
        "detail",
        "delivery_note",
        ("status", "proposed_total_pen"),
        "payment_link_expires_at",
        "created_at",
    )
    actions = ["send_payment_link"]

    @admin.action(description="Generar enlace de pago (72 h) y enviarlo al cliente")
    def send_payment_link(self, request, queryset):
        for quote in queryset.select_related("customer"):
            if not quote.proposed_total_pen or quote.proposed_total_pen <= 0:
                self.message_user(
                    request, f"Cotización {quote.pk}: define el monto primero.", messages.ERROR
                )
                continue
            if hasattr(quote, "order"):
                self.message_user(
                    request, f"Cotización {quote.pk}: ya tiene pedido.", messages.WARNING
                )
                continue
            quote.issue_payment_link(settings.QUOTE_PAYMENT_LINK_HOURS)
            quote.save()
            pay_url = f"{settings.SITE_URL}/cotizar/pagar/{quote.payment_token}/"
            notifications.send(
                "quote_link",
                {"quote": quote, "pay_url": pay_url},
                to=[quote.customer.email],
                subject=f"Tu cotización AltoTec #{quote.pk}",
            )
            self.message_user(request, f"Cotización {quote.pk}: enlace enviado ({pay_url}).")
