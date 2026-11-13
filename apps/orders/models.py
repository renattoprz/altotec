import secrets
from decimal import Decimal

from django.core.validators import RegexValidator
from django.db import models

from apps.audit.models import AuditedModel
from apps.catalog.models import Product
from apps.customers.models import Customer


def new_tracking_token() -> str:
    return secrets.token_urlsafe(32)


def new_order_code() -> str:
    return "AT-" + secrets.token_hex(4).upper()


class ShippingZone(AuditedModel):
    AUDIT_FIELDS = ("price_pen", "lead_time_days", "active")

    name = models.CharField("zona", max_length=60, unique=True)
    departments = models.JSONField(
        "códigos ubigeo (2 dígitos departamento o 4 dígitos provincia)", default=list, blank=True
    )
    price_pen = models.DecimalField("tarifa (S/)", max_digits=8, decimal_places=2)
    lead_time_days = models.PositiveSmallIntegerField("plazo (días)")
    active = models.BooleanField("activa", default=True)

    class Meta:
        verbose_name = "zona de envío"
        verbose_name_plural = "zonas de envío"

    def __str__(self):
        return self.name


class Order(AuditedModel):
    class Status(models.TextChoices):
        PENDING_PAYMENT = "pending_payment", "Pendiente de pago"
        PAID = "paid", "Pagado"
        PREPARING = "preparing", "En preparación"
        SHIPPED = "shipped", "Enviado"
        DELIVERED = "delivered", "Entregado"
        CANCELLED = "cancelled", "Anulado"
        REFUNDED = "refunded", "Reembolsado"

    class Receipt(models.TextChoices):
        BOLETA = "boleta", "Boleta"
        FACTURA = "factura", "Factura"

    class Delivery(models.TextChoices):
        HOME = "home", "Envío a domicilio"
        AGENCY = "agency", "Recojo en agencia"

    AUDIT_FIELDS = ("status", "total_pen", "courier", "tracking_number")

    code = models.CharField(max_length=12, unique=True, default=new_order_code, editable=False)
    tracking_token = models.CharField(
        max_length=64, unique=True, default=new_tracking_token, editable=False
    )
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="orders")
    quote = models.OneToOneField(
        "quotes.Quote", null=True, blank=True, on_delete=models.PROTECT, related_name="order"
    )
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING_PAYMENT)
    receipt_type = models.CharField("comprobante", max_length=7, choices=Receipt.choices)
    receipt_number = models.CharField("número de comprobante", max_length=20, blank=True)

    delivery = models.CharField("modalidad", max_length=6, choices=Delivery.choices)
    address = models.CharField("dirección o agencia de destino", max_length=250)
    district = models.CharField("distrito", max_length=80, blank=True)
    reference = models.CharField("referencia", max_length=200, blank=True)
    ubigeo = models.CharField(
        max_length=6, validators=[RegexValidator(r"^\d{6}$", "Ubigeo inválido.")]
    )
    shipping_zone = models.ForeignKey(ShippingZone, on_delete=models.PROTECT)
    courier = models.CharField(max_length=60, blank=True)
    tracking_number = models.CharField("número de guía", max_length=60, blank=True)

    subtotal_pen = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    shipping_pen = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("0"))
    total_pen = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    paid_at = models.DateTimeField("pagado el", null=True, blank=True)
    receipt_error = models.CharField("error al emitir comprobante", max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "pedido"

    def __str__(self):
        return self.code

    @property
    def total_cents(self) -> int:
        return int((self.total_pen * 100).to_integral_value())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField("cantidad")
    unit_price_pen = models.DecimalField("precio unitario (S/)", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "línea de pedido"

    def __str__(self):
        return f"{self.quantity} × {self.product_id}"

    @property
    def line_total(self) -> Decimal:
        return self.unit_price_pen * self.quantity


class Payment(AuditedModel):
    """Cobro en Culqi. Nunca se guardan datos de tarjeta: solo el id del cargo."""

    class Status(models.TextChoices):
        CREATED = "created", "Creado"
        SUCCEEDED = "succeeded", "Exitoso"
        FAILED = "failed", "Fallido"
        REFUNDED = "refunded", "Reembolsado"

    AUDIT_FIELDS = ("status",)

    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="payments")
    culqi_charge_id = models.CharField(max_length=64, unique=True)
    amount_cents = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.CREATED)
    webhook_received_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "pago"

    def __str__(self):
        return self.culqi_charge_id
