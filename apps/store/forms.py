import re

from django import forms

from apps.core.ubigeo import DEPARTMENTS, LIMA_PROVINCES, build_ubigeo
from apps.customers.models import Customer
from apps.orders.models import Order

DOC_PATTERNS = {"dni": r"^\d{8}$", "ce": r"^[0-9A-Za-z]{9,12}$", "ruc": r"^(10|15|17|20)\d{9}$"}
PHONE_PATTERN = r"^9\d{8}$"


class CustomerFieldsMixin(forms.Form):
    doc_type = forms.ChoiceField(label="Tipo de documento", choices=Customer.DocType.choices)
    doc_number = forms.CharField(label="Número de documento", max_length=12)
    full_name = forms.CharField(label="Nombre completo o razón social", max_length=200)
    email = forms.EmailField(label="Correo electrónico")
    phone = forms.CharField(label="Celular", max_length=9, help_text="9 dígitos, empieza con 9")

    def clean_phone(self):
        phone = re.sub(r"\D", "", self.cleaned_data["phone"])
        if not re.match(PHONE_PATTERN, phone):
            raise forms.ValidationError("Ingresa un celular válido de 9 dígitos.")
        return phone

    def clean_customer_doc(self, cleaned):
        doc_type, number = cleaned.get("doc_type"), cleaned.get("doc_number", "").strip()
        if doc_type and number and not re.match(DOC_PATTERNS[doc_type], number):
            self.add_error("doc_number", "El número no corresponde al tipo de documento.")
        cleaned["doc_number"] = number
        return cleaned


class AddressFieldsMixin(forms.Form):
    delivery = forms.ChoiceField(
        label="¿Cómo lo recibes?",
        choices=Order.Delivery.choices,
        widget=forms.RadioSelect,
        initial=Order.Delivery.HOME,
    )
    department = forms.ChoiceField(label="Departamento", choices=[("", "Elige")] + DEPARTMENTS)
    lima_province = forms.ChoiceField(
        label="Provincia de Lima", choices=[("", "Elige")] + LIMA_PROVINCES, required=False
    )
    district = forms.CharField(label="Distrito", max_length=80)
    address = forms.CharField(
        label="Dirección o agencia de destino",
        max_length=250,
        help_text="Si eliges recojo en agencia, escribe la agencia y sede (ej. Shalom Arequipa).",
    )
    reference = forms.CharField(label="Referencia", max_length=200, required=False)
    receipt_type = forms.ChoiceField(
        label="Comprobante",
        choices=Order.Receipt.choices,
        widget=forms.RadioSelect,
        initial=Order.Receipt.BOLETA,
    )

    def clean_address_block(self, cleaned):
        try:
            cleaned["ubigeo"] = build_ubigeo(
                cleaned.get("department", ""), cleaned.get("lima_province")
            )
        except ValueError as exc:
            field = "lima_province" if cleaned.get("department") == "15" else "department"
            self.add_error(field, str(exc))
        return cleaned


class CheckoutForm(CustomerFieldsMixin, AddressFieldsMixin):
    accept_terms = forms.BooleanField(
        label="Acepto los términos y condiciones y la política de privacidad", required=True
    )
    marketing_consent = forms.BooleanField(
        label="Quiero recibir ofertas por correo (opcional)", required=False
    )

    field_order = [
        "doc_type",
        "doc_number",
        "full_name",
        "email",
        "phone",
        "receipt_type",
        "delivery",
        "department",
        "lima_province",
        "district",
        "address",
        "reference",
        "accept_terms",
        "marketing_consent",
    ]

    def clean(self):
        cleaned = super().clean()
        self.clean_customer_doc(cleaned)
        self.clean_address_block(cleaned)
        if (
            cleaned.get("receipt_type") == Order.Receipt.FACTURA
            and cleaned.get("doc_type") != "ruc"
        ):
            self.add_error("doc_type", "Para factura necesitas RUC.")
        return cleaned


class QuotePaymentForm(AddressFieldsMixin):
    accept_terms = forms.BooleanField(
        label="Acepto los términos y condiciones y la política de privacidad", required=True
    )

    def __init__(self, *args, quote=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.quote = quote

    def clean(self):
        cleaned = super().clean()
        self.clean_address_block(cleaned)
        if (
            cleaned.get("receipt_type") == Order.Receipt.FACTURA
            and self.quote
            and self.quote.customer.doc_type != "ruc"
        ):
            self.add_error("receipt_type", "La cotización no se registró con RUC.")
        return cleaned
