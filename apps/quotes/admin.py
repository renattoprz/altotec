from django.contrib import admin

from .models import Quote


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "business_type",
        "registers",
        "status",
        "proposed_total_pen",
        "created_at",
    )
    list_filter = ("status",)
