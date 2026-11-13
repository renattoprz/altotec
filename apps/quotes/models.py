from django.db import models

from apps.audit.models import AuditedModel
from apps.customers.models import Customer


class Quote(AuditedModel):
    class Status(models.TextChoices):
        NEW = "new", "Nueva"
        SENT = "sent", "Enviada al cliente"
        ACCEPTED = "accepted", "Aceptada (enlace de pago)"
        EXPIRED = "expired", "Vencida"
        REJECTED = "rejected", "Rechazada"

    AUDIT_FIELDS = ("status", "proposed_total_pen")

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="quotes")
    business_type = models.CharField("rubro", max_length=80)
    registers = models.PositiveSmallIntegerField("número de cajas", default=1)
    detail = models.TextField("detalle")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.NEW)
    proposed_total_pen = models.DecimalField(
        "monto propuesto (S/)", max_digits=12, decimal_places=2, null=True, blank=True
    )
    payment_link_expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "cotización"
        verbose_name_plural = "cotizaciones"

    def __str__(self):
        return f"Cotización {self.pk}"
