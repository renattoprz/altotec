from django import forms

from apps.store.forms import CustomerFieldsMixin

from .models import Complaint


class ComplaintForm(CustomerFieldsMixin):
    consumer_address = forms.CharField(label="Domicilio", max_length=250)
    guardian_name = forms.CharField(
        label="Padre, madre o apoderado (solo si eres menor de edad)",
        max_length=200,
        required=False,
    )
    kind = forms.ChoiceField(
        label="Tipo",
        choices=Complaint.Kind.choices,
        widget=forms.RadioSelect,
        help_text="Reclamo: disconformidad con el producto o servicio. "
        "Queja: malestar por la atención recibida.",
    )
    order_code = forms.CharField(
        label="Código de pedido (si tienes)", max_length=12, required=False
    )
    product_or_service = forms.CharField(label="Producto o servicio", max_length=200)
    amount_pen = forms.DecimalField(
        label="Monto reclamado (S/)", max_digits=12, decimal_places=2, min_value=0, required=False
    )
    detail = forms.CharField(
        label="Detalle", max_length=3000, widget=forms.Textarea(attrs={"rows": 5})
    )
    request = forms.CharField(
        label="¿Qué solicitas?", max_length=2000, widget=forms.Textarea(attrs={"rows": 3})
    )
    accept = forms.BooleanField(
        label="Declaro que los datos son verdaderos y acepto que se usen para atender mi caso"
    )

    def clean(self):
        cleaned = super().clean()
        return self.clean_customer_doc(cleaned)
