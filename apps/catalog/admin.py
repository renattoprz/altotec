from django.contrib import admin

from .models import Category, Product, ProductImage, Supplier, SupplierOffer


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


class SupplierOfferInline(admin.TabularInline):
    model = SupplierOffer
    extra = 0
    readonly_fields = ("confirmed_at",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "category", "price_pen", "sale_mode", "published")
    list_filter = ("category", "sale_mode", "published", "brand")
    search_fields = ("sku", "name", "brand")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline, SupplierOfferInline]


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("business_name", "ruc", "active")
    search_fields = ("business_name", "ruc")
