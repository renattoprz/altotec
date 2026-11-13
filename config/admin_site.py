from django import forms
from django_otp.admin import OTPAdminAuthenticationForm, OTPAdminSite
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.models import TOTPDevice


class AltoTecLoginForm(OTPAdminAuthenticationForm):
    """Un solo paso: usuario, contraseña y código de 6 dígitos de la app autenticadora.

    No se pide elegir dispositivo: el código se verifica contra los dispositivos TOTP
    confirmados del propio usuario. Se ignora el botón de "desafío" (solo aplica a
    dispositivos por SMS/correo, que no usamos).
    """

    otp_token = forms.CharField(
        label="Código de verificación",
        required=False,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "one-time-code",
                "inputmode": "numeric",
                "pattern": "[0-9]*",
                "maxlength": "8",
            }
        ),
    )

    # Mensajes de error visibles, no credenciales: bandit B105 se dispara solo
    # porque las claves del diccionario contienen la palabra "token".
    otp_error_messages = {  # nosec B105
        **OTPAdminAuthenticationForm.otp_error_messages,
        "token_required": "Ingresa el código de 6 dígitos de tu app autenticadora.",
        "invalid_token": "Código incorrecto o vencido. Inténtalo de nuevo.",
        "device_required": "Ingresa el código de 6 dígitos de tu app autenticadora.",
        "challenge_exception": "No se pudo verificar el código.",
        "not_interactive": "No se pudo verificar el código.",
        "challenge_message": "No se pudo verificar el código.",
        "n_failed_attempts": "Verificación bloqueada temporalmente por %(failure_count)d "
        "intentos fallidos. Inténtalo de nuevo en unos minutos.",
        "verification_not_allowed": "Demasiados intentos. Espera un momento e inténtalo de nuevo.",
    }

    def _chosen_device(self, user):
        # Elige el dispositivo del propio usuario según el formato del código:
        # 6 dígitos = app autenticadora (TOTP); otro formato = código de respaldo.
        token = (self.cleaned_data.get("otp_token") or "").strip()
        model = TOTPDevice if token.isdigit() and len(token) == 6 else StaticDevice
        return model.objects.filter(user=user, confirmed=True).order_by("pk").first()

    def clean(self):
        self.data = self.data.copy()
        self.data.pop("otp_challenge", None)
        self.data.pop("otp_device", None)
        return super().clean()


class AltoTecAdminSite(OTPAdminSite):
    """Panel de administración: exige contraseña + código TOTP (MFA obligatorio)."""

    site_header = "AltoTec · Administración"
    site_title = "AltoTec"
    index_title = "Gestión de la tienda"
    login_form = AltoTecLoginForm
    login_template = "admin/altotec_login.html"
