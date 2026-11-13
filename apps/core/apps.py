from django.apps import AppConfig, apps

# Nombres en español para el panel de apps de terceros sin traducción completa.
# (etiqueta de app, {modelo: (singular, plural)}, nombre de la sección)
THIRD_PARTY_LABELS = {
    "axes": (
        "Seguridad de acceso",
        {
            "accessattempt": ("intento de acceso fallido", "intentos de acceso fallidos"),
            "accessfailurelog": ("registro de fallo de acceso", "registros de fallos de acceso"),
            "accesslog": ("registro de acceso", "registros de acceso"),
        },
    ),
    "otp_totp": (
        "MFA · App autenticadora",
        {"totpdevice": ("dispositivo autenticador", "dispositivos autenticadores")},
    ),
    "otp_static": (
        "MFA · Códigos de respaldo",
        {
            "staticdevice": ("juego de códigos de respaldo", "juegos de códigos de respaldo"),
            "statictoken": ("código de respaldo", "códigos de respaldo"),
        },
    ),
    "auth": (
        "Usuarios y permisos",
        {"user": ("usuario", "usuarios"), "group": ("grupo", "grupos")},
    ),
}


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Núcleo"

    def ready(self):
        for label, (section, models) in THIRD_PARTY_LABELS.items():
            try:
                config = apps.get_app_config(label)
            except LookupError:
                continue
            config.verbose_name = section
            for model_name, (singular, plural) in models.items():
                try:
                    meta = config.get_model(model_name)._meta
                except LookupError:
                    continue
                meta.verbose_name = singular
                meta.verbose_name_plural = plural
