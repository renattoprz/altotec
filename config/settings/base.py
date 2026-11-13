"""Configuración base de AltoTec.

Toda configuración sensible se lee de variables de entorno (en producción las
inyecta DigitalOcean como variables cifradas). Nunca se guardan secretos en el repositorio.
Ver docs/security/ para el mapeo de controles a SOC 2 / ISO 27001 / ISO 27701.
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def env(name: str, default: str | None = None, *, required: bool = False) -> str:
    value = os.environ.get(name, default)
    if required and not value:
        raise ImproperlyConfigured(f"Falta la variable de entorno obligatoria {name}")
    return value or ""


def env_bool(name: str, default: bool = False) -> bool:
    return env(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in env(name, default).split(",") if item.strip()]


SECRET_KEY = env("DJANGO_SECRET_KEY", required=True)
DEBUG = False
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS")

INSTALLED_APPS = [
    "config.apps.AltoTecAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Seguridad
    "django_otp",
    "django_otp.plugins.otp_totp",
    "django_otp.plugins.otp_static",
    "axes",
    "csp",
    # Dominio
    "apps.core",
    "apps.audit",
    "apps.catalog",
    "apps.customers",
    "apps.orders",
    "apps.quotes",
    "apps.complaints",
    "apps.store",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
    "apps.audit.middleware.RequestContextMiddleware",
    # Axes debe ir al final.
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.store",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", "altotec"),
        "USER": env("DB_USER", "altotec_app"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST", "localhost"),
        "PORT": env("DB_PORT", "5432"),
        "CONN_MAX_AGE": 60,
        "CONN_HEALTH_CHECKS": True,
        "OPTIONS": {"sslmode": env("DB_SSLMODE", "require")},
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Autenticación ---------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 14},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Bloqueo por intentos fallidos (ISO 27001 A.8.5).
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # horas
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]
AXES_RESET_ON_SUCCESS = True

# --- Sesiones y cookies ----------------------------------------------------
# Cookies "host-only" (sin SESSION_COOKIE_DOMAIN): no se comparten con otros
# subdominios de codaltoperu.com.
SESSION_COOKIE_AGE = 8 * 60 * 60
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_NAME = "__Host-altotec_session"
CSRF_COOKIE_NAME = "__Host-altotec_csrf"
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"

# --- Cabeceras de seguridad ------------------------------------------------
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

CULQI_CHECKOUT_ORIGIN = "https://checkout.culqi.com"
CULQI_JS_ORIGIN = "https://js.culqi.com"
TURNSTILE_ORIGIN = "https://challenges.cloudflare.com"

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ["'self'"],
        "script-src": ["'self'", CULQI_JS_ORIGIN, CULQI_CHECKOUT_ORIGIN, TURNSTILE_ORIGIN],
        "style-src": ["'self'"],
        "img-src": ["'self'", "data:", env("MEDIA_ORIGIN", "'self'")],
        "connect-src": ["'self'", CULQI_CHECKOUT_ORIGIN],
        "frame-src": [CULQI_CHECKOUT_ORIGIN, TURNSTILE_ORIGIN],
        "frame-ancestors": ["'none'"],
        "form-action": ["'self'"],
        "base-uri": ["'none'"],
        "object-src": ["'none'"],
    }
}

# --- Internacionalización ---------------------------------------------------
LANGUAGE_CODE = "es-pe"
TIME_ZONE = "America/Lima"
USE_I18N = True
USE_TZ = True

# --- Archivos estáticos -----------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
# Archivos servidos en la raíz del sitio (favicon.ico, apple-touch-icon, manifiesto).
WHITENOISE_ROOT = BASE_DIR / "static" / "root"
WHITENOISE_MIMETYPES = {".webmanifest": "application/manifest+json"}
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# Límite de tamaño de peticiones (mitiga abuso).
DATA_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024
DATA_UPLOAD_MAX_NUMBER_FIELDS = 200

# --- Integraciones ----------------------------------------------------------
CULQI_PUBLIC_KEY = env("CULQI_PUBLIC_KEY")
CULQI_SECRET_KEY = env("CULQI_SECRET_KEY")
CULQI_API_BASE = env("CULQI_API_BASE", "https://api.culqi.com/v2")
# Secreto compartido que se configura en la URL del webhook en el panel de Culqi.
CULQI_WEBHOOK_TOKEN = env("CULQI_WEBHOOK_TOKEN")

ALTOFACT_API_BASE = env("ALTOFACT_API_BASE")
ALTOFACT_API_TOKEN = env("ALTOFACT_API_TOKEN")

TURNSTILE_SITE_KEY = env("TURNSTILE_SITE_KEY")
TURNSTILE_SECRET_KEY = env("TURNSTILE_SECRET_KEY")

# --- Registro (sin datos personales) ----------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"redact_pii": {"()": "apps.audit.logging.RedactPIIFilter"}},
    "formatters": {
        "json": {
            "format": '{"time":"%(asctime)s","level":"%(levelname)s",'
            '"logger":"%(name)s","msg":"%(message)s"}'
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "filters": ["redact_pii"],
        }
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {"axes": {"level": "WARNING"}},
}

ADMIN_URL = env("DJANGO_ADMIN_URL", "gestion-altotec/")

# --- Caché (límite de solicitudes). En producción: tabla en PostgreSQL,
# compartida entre todos los procesos (python manage.py createcachetable).
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache",
    }
}

# --- Correo -----------------------------------------------------------------
EMAIL_BACKEND = env("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = int(env("EMAIL_PORT", "587"))
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 10
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "AltoTec <ventas@codaltoperu.com>")

# --- Tienda -----------------------------------------------------------------
SITE_URL = env("SITE_URL", "https://tec.codaltoperu.com")
STORE_ADMIN_EMAILS = env_list("STORE_ADMIN_EMAILS")
STORE_WHATSAPP = env("STORE_WHATSAPP")  # solo dígitos, con código de país: 51999999999
POLICY_VERSION = "2026-11-v1"
QUOTE_PAYMENT_LINK_HOURS = 72
# Pago simulado (sin Culqi) solo para desarrollo local; nunca en producción.
FAKE_PAYMENTS = False
