from django.contrib import admin

from .models import Consent, Customer, DataSubjectRequest


class ConsentInline(admin.TabularInline):
    model = Consent
    extra = 0
    can_delete = False
    readonly_fields = ("purpose", "granted", "policy_version", "ip", "created_at")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "doc_type", "doc_number", "created_at")
    search_fields = ("doc_number", "full_name")
    inlines = [ConsentInline]


@admin.register(DataSubjectRequest)
class DataSubjectRequestAdmin(admin.ModelAdmin):
    list_display = ("kind", "created_at", "resolved_at")
    list_filter = ("kind",)
