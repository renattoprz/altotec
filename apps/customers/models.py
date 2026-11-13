from django.core.validators import RegexValidator
from django.db import models


class Customer(models.Model):
    """Comprador. Contiene datos personales (Ley 29733): acceso solo desde el panel."""

    class DocType(models.TextChoices):
        DNI = "dni", "DNI"
        CE = "ce", "Carné de extranjería"
        RUC = "ruc", "RUC"

    doc_type = models.CharField("tipo de documento", max_length=3, choices=DocType.choices)
    doc_number = models.CharField(
        "número de documento",
        max_length=12,
        validators=[RegexValidator(r"^[0-9A-Za-z]{8,12}$", "Documento inválido.")],
    )
    full_name = models.CharField("nombre o razón social", max_length=200)
    email = models.EmailField("correo")
    phone = models.CharField("teléfono", max_length=20)
    marketing_consent = models.BooleanField("acepta publicidad", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "cliente"
        indexes = [models.Index(fields=["doc_type", "doc_number"])]

    def __str__(self):
        return f"{self.get_doc_type_display()} {self.doc_number}"


class Consent(models.Model):
    """Evidencia de cada consentimiento otorgado (Ley 29733 art. 13-14, ISO 27701 7.2.3)."""

    class Purpose(models.TextChoices):
        TERMS = "terms", "Términos y condiciones"
        PRIVACY = "privacy", "Tratamiento de datos para el pedido"
        MARKETING = "marketing", "Publicidad"

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="consents")
    purpose = models.CharField(max_length=12, choices=Purpose.choices)
    granted = models.BooleanField()
    policy_version = models.CharField("versión de la política", max_length=20)
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "consentimiento"

    def __str__(self):
        return f"{self.get_purpose_display()}: {'sí' if self.granted else 'no'}"


class DataSubjectRequest(models.Model):
    """Solicitudes ARCO (acceso, rectificación, cancelación, oposición)."""

    class Kind(models.TextChoices):
        ACCESS = "access", "Acceso"
        RECTIFY = "rectify", "Rectificación"
        CANCEL = "cancel", "Cancelación"
        OPPOSE = "oppose", "Oposición"

    email = models.EmailField("correo")
    kind = models.CharField("tipo", max_length=8, choices=Kind.choices)
    detail = models.TextField("detalle")
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    response = models.TextField("respuesta", blank=True)

    class Meta:
        verbose_name = "solicitud ARCO"
        verbose_name_plural = "solicitudes ARCO"

    def __str__(self):
        return f"{self.get_kind_display()} {self.created_at:%Y-%m-%d}"
