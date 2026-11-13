from django_otp.admin import OTPAdminSite


class AltoTecAdminSite(OTPAdminSite):
    """Panel de administración: exige contraseña + código TOTP (MFA obligatorio)."""

    site_header = "AltoTec · Administración"
    site_title = "AltoTec"
    index_title = "Gestión de la tienda"
