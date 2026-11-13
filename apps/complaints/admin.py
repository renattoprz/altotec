from django.contrib import admin, messages
from django.utils import timezone

from apps.core import notifications

from .models import Complaint


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("__str__", "kind", "created_at", "due_date", "responded_at")
    list_filter = ("kind",)
    readonly_fields = (
        "number",
        "customer",
        "kind",
        "consumer_address",
        "guardian_name",
        "order_code",
        "product_or_service",
        "amount_pen",
        "detail",
        "request",
        "created_at",
        "due_date",
        "responded_at",
    )
    actions = ["send_response"]

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description="Enviar respuesta al consumidor")
    def send_response(self, request, queryset):
        for complaint in queryset.select_related("customer"):
            if not complaint.response.strip():
                self.message_user(
                    request, f"{complaint}: escribe la respuesta primero.", messages.ERROR
                )
                continue
            complaint.responded_at = timezone.now()
            complaint.save()
            notifications.send(
                "complaint_response",
                {"complaint": complaint},
                to=[complaint.customer.email],
                subject=f"Respuesta a su {complaint.get_kind_display().lower()} {complaint}",
            )
            self.message_user(request, f"{complaint}: respuesta enviada.")
