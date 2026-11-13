from django import forms

from apps.store.forms import CustomerFieldsMixin


class QuoteRequestForm(CustomerFieldsMixin):
    business_type = forms.ChoiceField(
        label="Tipo de negocio",
        choices=[
            ("", "Elige"),
            ("Bodega o minimarket", "Bodega o minimarket"),
            ("Restaurante o cafetería", "Restaurante o cafetería"),
            ("Tienda de ropa o calzado", "Tienda de ropa o calzado"),
            ("Farmacia", "Farmacia"),
            ("Ferretería", "Ferretería"),
            ("Otro", "Otro"),
        ],
    )
    registers = forms.IntegerField(label="¿Cuántas cajas?", min_value=1, max_value=50, initial=1)
    delivery_note = forms.CharField(label="Ciudad de entrega", max_length=120)
    detail = forms.CharField(
        label="¿Qué necesitas?",
        max_length=2000,
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text="Cuéntanos qué equipos te interesan o qué problema quieres resolver.",
    )
    accept_terms = forms.BooleanField(
        label="Acepto la política de privacidad para que me contacten con la cotización"
    )

    field_order = [
        "business_type",
        "registers",
        "detail",
        "delivery_note",
        "doc_type",
        "doc_number",
        "full_name",
        "email",
        "phone",
        "accept_terms",
    ]

    def clean(self):
        cleaned = super().clean()
        return self.clean_customer_doc(cleaned)
