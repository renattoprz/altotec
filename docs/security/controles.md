# Mapa de controles

| # | Control | Implementación / evidencia | SOC 2 | ISO 27001:2022 | ISO 27701 / Ley 29733 |
| --- | --- | --- | --- | --- | --- |
| 1 | Sin datos de tarjeta | Culqi Checkout tokeniza en el navegador; solo se guarda `culqi_charge_id` (`apps/orders/models.py`) | CC6.1 | A.8.24 | — |
| 2 | Verificación de pagos | El webhook vuelve a consultar el cargo en la API y compara el monto (`apps/orders/webhooks.py`, pruebas en `test_webhook.py`) | PI1.2 | A.8.28 | — |
| 3 | Precios en servidor | `apps/orders/pricing.py` ignora montos del navegador (`test_pricing.py`) | PI1.2 | A.8.28 | — |
| 4 | MFA en panel | `OTPAdminSite` (`config/admin_site.py`, `test_security.py`) | CC6.1 | A.8.5 | — |
| 5 | Bloqueo por intentos | django-axes, 5 intentos / 1 h (`config/settings/base.py`) | CC6.1 | A.8.5 | — |
| 6 | URL del panel no estándar | `DJANGO_ADMIN_URL` | CC6.6 | A.8.20 | — |
| 7 | Cabeceras de seguridad | HSTS 1 año + subdominios, CSP estricta, X-Frame-Options DENY (`config/settings/prod.py`) | CC6.6 | A.8.26 | — |
| 8 | Aislamiento entre apps | Cookies `__Host-` sin dominio compartido; BD y llaves por app | CC6.1 | A.8.22 | 7.4.5 |
| 9 | Hash de contraseñas | Argon2 | CC6.1 | A.8.24 | — |
| 10 | Auditoría inmutable | `apps/audit` (no se puede editar ni borrar; `test_audit.py`) | CC7.2 | A.8.15 | 6.13 |
| 11 | Logs sin datos personales | `RedactPIIFilter` (`apps/audit/logging.py`) | C1.1 | A.8.15 | Minimización |
| 12 | Secretos | Variables cifradas de DigitalOcean; `.gitignore` de credenciales; gitleaks en CI | CC6.1 | A.5.17, A.8.4 | — |
| 13 | Desarrollo seguro | Ruff (reglas S), Bandit, pip-audit, `check --deploy` en CI | CC8.1 | A.8.25, A.8.28 | — |
| 14 | Gestión de cambios | Rama protegida, PR + CI obligatorios | CC8.1 | A.8.32 | — |
| 15 | Contenedor sin root | `USER 10001` en `Dockerfile` | CC6.8 | A.8.2 | — |
| 16 | Perímetro | Cloudflare WAF, rate limiting, Turnstile en formularios | CC6.6 | A.8.20, A.8.23 | — |
| 17 | Respaldos | Volcado diario cifrado a R2 + prueba mensual | A1.2 | A.8.13 | — |
| 18 | Monitoreo | Sentry (errores), UptimeRobot (disponibilidad) | CC7.2, A1.1 | A.8.16 | — |
| 19 | Consentimiento | Modelo `Consent` con versión de política e IP | P2.1 | — | Art. 13–14; 7.2.3 |
| 20 | Derechos ARCO | Modelo `DataSubjectRequest` | P5.1 | — | 7.3 |
| 21 | Retención | Ver privacidad.md | P4.2 | A.5.33 | 7.4.7 |
| 22 | Incidentes | respuesta-incidentes.md | CC7.3–CC7.5 | A.5.24–A.5.27 | 6.13 |
| 23 | Libro de Reclamaciones | `apps/complaints` con plazo de 15 días hábiles | — | — | Código del Consumidor |

Estado: controles 1–15 y 19–23 implementados en el código base; 16–18 se activan en el despliegue.
