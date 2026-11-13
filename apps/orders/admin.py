from django.contrib import admin

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
    list_display = ("code", "status", "total_pen", "delivery", "created_at")
    list_filter = ("status", "delivery", "receipt_type")
    search_fields = ("code", "tracking_number")
    readonly_fields = (
        "code",
        "customer",
        "receipt_type",
        "subtotal_pen",
        "shipping_pen",
        "total_pen",
        "address",
        "ubigeo",
        "shipping_zone",
        "delivery",
        "created_at",
    )
    inlines = [OrderItemInline, PaymentInline]

    def has_delete_permission(self, request, obj=None):
        return False  # pedidos se anulan, no se borran (obligación tributaria)


@admin.register(ShippingZone)
class ShippingZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "price_pen", "lead_time_days", "active")
