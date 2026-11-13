from datetime import date, timedelta

from django.db import models

from apps.audit.models import AuditedModel
from apps.customers.models import Customer

RESPONSE_BUSINESS_DAYS = 15


def add_business_days(start: date, days: int) -> date:
    current = start
    while days > 0:
        current += timedelta(days=1)
        if current.weekday() < 5:
            days -= 1
    return current


class Complaint(AuditedModel):
    """Libro de Reclamaciones virtual (Código de Protección y Defensa del Consumidor)."""

    class Kind(models.TextChoices):
        RECLAMO = "reclamo", "Reclamo"
        QUEJA = "queja", "Queja"

    AUDIT_FIELDS = ("response", "responded_at")

    number = models.PositiveIntegerField("correlativo", unique=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="complaints")
    kind = models.CharField("tipo", max_length=7, choices=Kind.choices)
    consumer_address = models.CharField("domicilio del consumidor", max_length=250, default="")
    guardian_name = models.CharField(
        "padre, madre o apoderado (si es menor de edad)", max_length=200, blank=True
    )
    order_code = models.CharField("código de pedido", max_length=12, blank=True)
    product_or_service = models.CharField("bien o servicio", max_length=200)
    amount_pen = models.DecimalField(
        "monto reclamado (S/)", max_digits=12, decimal_places=2, null=True, blank=True
    )
    detail = models.TextField("detalle")
    request = models.TextField("pedido del consumidor")
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField("fecha límite de respuesta", editable=False)
    response = models.TextField("respuesta", blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-number"]
        verbose_name = "reclamo"

    def save(self, *args, **kwargs):
        if self.pk is None:
            last = Complaint.objects.order_by("-number").values_list("number", flat=True).first()
            self.number = (last or 0) + 1
            self.due_date = add_business_days(date.today(), RESPONSE_BUSINESS_DAYS)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Hoja N.° {self.number:06d}"
