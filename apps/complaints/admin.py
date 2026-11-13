from django.contrib import admin

from .models import Complaint


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("__str__", "kind", "created_at", "due_date", "responded_at")
    list_filter = ("kind",)
    readonly_fields = (
        "number",
        "customer",
        "kind",
        "product_or_service",
        "amount_pen",
        "detail",
        "request",
        "created_at",
        "due_date",
    )

    def has_delete_permission(self, request, obj=None):
        return False
