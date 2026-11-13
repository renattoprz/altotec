from django import forms

from .models import DataSubjectRequest


class ArcoForm(forms.ModelForm):
    class Meta:
        model = DataSubjectRequest
        fields = ["email", "kind", "detail"]
        widgets = {"detail": forms.Textarea(attrs={"rows": 4})}
        labels = {
            "email": "Correo con el que compraste",
            "kind": "Derecho que ejerces",
            "detail": "Detalle de tu solicitud",
        }
