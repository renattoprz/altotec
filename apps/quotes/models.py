import secrets
from datetime import timedelta

from django.db import models
from django.utils import timezone

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
    payment_token = models.CharField(
        max_length=64, unique=True, null=True, blank=True, editable=False
    )
    payment_link_expires_at = models.DateTimeField(null=True, blank=True)
    delivery_note = models.CharField("entrega (ciudad)", max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "cotización"
        verbose_name_plural = "cotizaciones"

    def __str__(self):
        return f"Cotización {self.pk}"

    def issue_payment_link(self, hours: int) -> None:
        self.payment_token = secrets.token_urlsafe(32)
        self.payment_link_expires_at = timezone.now() + timedelta(hours=hours)
        self.status = self.Status.ACCEPTED

    @property
    def payment_link_valid(self) -> bool:
        return bool(
            self.payment_token
            and self.proposed_total_pen
            and self.payment_link_expires_at
            and self.payment_link_expires_at > timezone.now()
            and self.status == self.Status.ACCEPTED
        )
