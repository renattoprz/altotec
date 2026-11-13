from django.contrib import admin, messages
from django.db import transaction

from . import altofact, services
from .models import Order, OrderItem, Payment, ShippingZone


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "unit_price_pen")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    can_delete = False
    readonly_fields = ("culqi_charge_id", "amount_cents", "status", "webhook_received_at")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("code", "status", "total_pen", "delivery", "receipt_number", "created_at")
    list_filter = ("status", "delivery", "receipt_type", "shipping_zone")
    search_fields = ("code", "tracking_number", "customer__doc_number")
    date_hierarchy = "created_at"
    readonly_fields = (
        "code",
        "customer",
        "quote",
        "receipt_type",
        "subtotal_pen",
        "shipping_pen",
        "total_pen",
        "address",
        "district",
        "reference",
        "ubigeo",
        "shipping_zone",
        "delivery",
        "paid_at",
        "receipt_error",
        "created_at",
    )
    fields = (
        ("code", "status"),
        ("customer", "quote"),
        ("receipt_type", "receipt_number", "receipt_error"),
        ("delivery", "shipping_zone"),
        "address",
        ("district", "reference", "ubigeo"),
        ("courier", "tracking_number"),
        ("subtotal_pen", "shipping_pen", "total_pen"),
        ("paid_at", "created_at"),
    )
    inlines = [OrderItemInline, PaymentInline]
    actions = ["mark_preparing", "mark_shipped", "mark_delivered", "emit_receipt"]

    def has_delete_permission(self, request, obj=None):
        return False  # pedidos se anulan, no se borran (obligación tributaria)

    @admin.action(description="Marcar como en preparación")
    def mark_preparing(self, request, queryset):
        updated = 0
        for order in queryset.filter(status=Order.Status.PAID):
            order.status = Order.Status.PREPARING
            order.save()
            updated += 1
        self.message_user(request, f"{updated} pedido(s) en preparación.")

    @admin.action(description="Marcar como enviado y avisar al cliente")
    def mark_shipped(self, request, queryset):
        for order in queryset.filter(status__in=[Order.Status.PAID, Order.Status.PREPARING]):
            if not (order.courier and order.tracking_number):
                self.message_user(
                    request, f"{order.code}: falta courier o número de guía.", messages.ERROR
                )
                continue
            order.status = Order.Status.SHIPPED
            order.save()
            transaction.on_commit(lambda o=order: services.notify_shipped(o))
            self.message_user(request, f"{order.code}: enviado y cliente notificado.")

    @admin.action(description="Marcar como entregado")
    def mark_delivered(self, request, queryset):
        updated = 0
        for order in queryset.filter(status=Order.Status.SHIPPED):
            order.status = Order.Status.DELIVERED
            order.save()
            updated += 1
        self.message_user(request, f"{updated} pedido(s) entregados.")

    @admin.action(description="Emitir comprobante en AltoFact")
    def emit_receipt(self, request, queryset):
        for order in queryset.exclude(status=Order.Status.PENDING_PAYMENT).filter(
            receipt_number=""
        ):
            try:
                order.receipt_number = altofact.emit_receipt(order)
                order.receipt_error = ""
                self.message_user(request, f"{order.code}: comprobante {order.receipt_number}.")
            except altofact.AltoFactError as exc:
                order.receipt_error = str(exc)[:250]
                self.message_user(request, f"{order.code}: {exc}", messages.WARNING)
            order.save()


@admin.register(ShippingZone)
class ShippingZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "price_pen", "lead_time_days", "active")
    list_editable = ("price_pen", "lead_time_days", "active")
