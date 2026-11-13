from datetime import timedelta
from decimal import Decimal

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone

from apps.audit.models import AuditedModel

ruc_validator = RegexValidator(r"^(10|15|17|20)\d{9}$", "RUC inválido.")


class Category(models.Model):
    name = models.CharField("nombre", max_length=80, unique=True)
    slug = models.SlugField(unique=True)
    order = models.PositiveSmallIntegerField("orden", default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "categoría"

    def __str__(self):
        return self.name


class Supplier(AuditedModel):
    AUDIT_FIELDS = ("business_name", "ruc", "contact_email", "active")

    business_name = models.CharField("razón social", max_length=200)
    ruc = models.CharField(max_length=11, unique=True, validators=[ruc_validator])
    contact_name = models.CharField("contacto", max_length=120, blank=True)
    contact_email = models.EmailField("correo", blank=True)
    contact_phone = models.CharField("teléfono", max_length=20, blank=True)
    terms = models.TextField("condiciones", blank=True)
    active = models.BooleanField("activo", default=True)

    class Meta:
        verbose_name = "proveedor"
        verbose_name_plural = "proveedores"

    def __str__(self):
        return self.business_name


class Product(AuditedModel):
    class SaleMode(models.TextChoices):
        ONLINE = "online", "Compra online"
        QUOTE = "quote", "Bajo cotización"

    AUDIT_FIELDS = ("price_pen", "sale_mode", "published")

    sku = models.CharField(max_length=40, unique=True)
    name = models.CharField("nombre", max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    brand = models.CharField("marca", max_length=80, blank=True)
    description = models.TextField("descripción", blank=True)
    specs = models.JSONField("especificaciones", default=dict, blank=True)
    price_pen = models.DecimalField(
        "precio (S/, IGV incluido)",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    sale_mode = models.CharField("modo de venta", max_length=10, choices=SaleMode.choices)
    lead_time_days = models.PositiveSmallIntegerField("plazo de entrega (días)", default=3)
    warranty_months = models.PositiveSmallIntegerField("garantía (meses)", default=12)
    published = models.BooleanField("publicado", default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "name"]
        verbose_name = "producto"

    def __str__(self):
        return f"{self.sku} · {self.name}"

    @property
    def can_buy_online(self) -> bool:
        """Solo se vende online si un proveedor confirmó stock recientemente."""
        return (
            self.published
            and self.sale_mode == self.SaleMode.ONLINE
            and self.offers.confirmed_recently().exists()
        )


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    url = models.URLField("URL (Cloudflare R2)")
    alt = models.CharField("texto alternativo", max_length=160, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "imagen"
        verbose_name_plural = "imágenes"

    def __str__(self):
        return self.alt or self.url


class SupplierOfferQuerySet(models.QuerySet):
    STOCK_FRESHNESS = timedelta(days=2)

    def confirmed_recently(self):
        return self.filter(
            stock_confirmed=True,
            confirmed_at__gte=timezone.now() - self.STOCK_FRESHNESS,
            supplier__active=True,
        )


class SupplierOffer(AuditedModel):
    AUDIT_FIELDS = ("cost_pen", "stock_confirmed")

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="offers")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="offers")
    cost_pen = models.DecimalField("costo (S/)", max_digits=10, decimal_places=2)
    stock_confirmed = models.BooleanField("stock confirmado", default=False)
    confirmed_at = models.DateTimeField("confirmado el", null=True, blank=True)

    objects = SupplierOfferQuerySet.as_manager()

    class Meta:
        unique_together = [("product", "supplier")]
        verbose_name = "oferta de proveedor"
        verbose_name_plural = "ofertas de proveedores"

    def save(self, *args, **kwargs):
        if self.stock_confirmed and self.confirmed_at is None:
            self.confirmed_at = timezone.now()
        super().save(*args, **kwargs)
