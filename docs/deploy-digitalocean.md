# Despliegue en DigitalOcean

Producción de AltoTec corre en **DigitalOcean**, detrás de **Cloudflare** (DNS, WAF,
caché y TLS). Esta guía cubre la opción recomendada y una alternativa más barata.

## Opción recomendada: App Platform + PostgreSQL administrado

| Pieza | Plan sugerido | Costo aprox. |
| --- | --- | --- |
| App Platform (servicio web desde este repo, Dockerfile) | Basic 1 vCPU / 512 MB | ~US$5/mes |
| Managed PostgreSQL 16 | 1 GB, 1 nodo | ~US$15/mes |
| Cloudflare | Free | US$0 |

Ventajas: TLS, despliegue en cada merge a `main`, reinicio automático, backups
diarios de BD con restauración a un punto en el tiempo, sin servidor que parchar.

### Pasos

1. **Base de datos:** Databases → Create → PostgreSQL 16, región `nyc` o `sfo`.
   Crear la BD `altotec` y el usuario `altotec_app`. En *Trusted sources* agregar
   solo la app (nunca "todas las IP").
2. **App:** Apps → Create → GitHub → `renattoprz/altotec`, rama `main`,
   *Autodeploy* activado. Tipo: Web Service con Dockerfile. Puerto HTTP: `8080`.
   Health check: ruta `/healthz`.
3. **Variables de entorno** (marcar como *Encrypted* las secretas):

   | Variable | Valor |
   | --- | --- |
   | `DJANGO_SECRET_KEY` 🔒 | `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
   | `DJANGO_ALLOWED_HOSTS` | `tec.codaltoperu.com` |
   | `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://tec.codaltoperu.com` |
   | `DJANGO_ADMIN_URL` 🔒 | ruta difícil de adivinar, p. ej. `panel-8f3k2/` |
   | `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` 🔒 | de la BD administrada |
   | `DB_SSLMODE` | `require` |
   | `RUN_MIGRATIONS` | `1` (migraciones y tabla de caché al arrancar) |
   | `CULQI_PUBLIC_KEY`, `CULQI_SECRET_KEY` 🔒, `CULQI_WEBHOOK_TOKEN` 🔒 | panel de Culqi |
   | `TURNSTILE_SITE_KEY`, `TURNSTILE_SECRET_KEY` 🔒 | panel de Cloudflare |
   | `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` 🔒 | proveedor SMTP |
   | `DEFAULT_FROM_EMAIL` | `AltoTec <ventas@codaltoperu.com>` |
   | `STORE_ADMIN_EMAILS` | correos que reciben avisos de pedidos |
   | `STORE_WHATSAPP` | `51` + número, solo dígitos |
   | `ALTOFACT_API_BASE`, `ALTOFACT_API_TOKEN` 🔒 | cuando AltoFact tenga API |

4. **Dominio:** en la app, Settings → Domains → `tec.codaltoperu.com`. En
   Cloudflare crear el CNAME que indique DigitalOcean, con proxy (nube naranja),
   SSL/TLS en modo **Full (strict)**.
5. **Primer usuario del panel** (consola de la app en DigitalOcean):
   `python manage.py createsuperuser` y luego `python manage.py setup_mfa <usuario>`
   (escanear el QR con Google Authenticator o similar).
6. **Webhook de Culqi:** en el panel de Culqi, URL
   `https://tec.codaltoperu.com/webhooks/culqi/<CULQI_WEBHOOK_TOKEN>/`.

## Alternativa económica: Droplet con Docker

Un Droplet de US$6/mes con Docker y PostgreSQL en el mismo servidor. Más barato,
pero tú administras parches, firewall y backups:

- Ubuntu LTS, acceso solo por llave SSH, `ufw` permitiendo 22 (desde tu IP) y 443
  solo desde los rangos de Cloudflare; actualizaciones automáticas de seguridad.
- `docker build -t altotec . && docker run --env-file /etc/altotec.env -p 127.0.0.1:8080:8080 altotec`
  detrás de Caddy o Nginx con certificado de origen de Cloudflare.
- Backup diario con `pg_dump` cifrado hacia un bucket fuera del Droplet
  (DigitalOcean Spaces o Cloudflare R2), probando la restauración cada mes.

## Entorno temporal (pruebas antes de producción)

Mientras no haya dominio ni llaves de Culqi, se puede publicar en App Platform con
la URL `*.ondigitalocean.app` (agregarla a `DJANGO_ALLOWED_HOSTS` y
`DJANGO_CSRF_TRUSTED_ORIGINS`), sin `CULQI_SECRET_KEY`: en producción el pago
simulado está **siempre desactivado**, así que el botón de pagar no cobrará hasta
cargar llaves de prueba de Culqi (`sk_test_…`).

## Checklist antes de abrir al público

- [ ] `python manage.py check --deploy` sin advertencias (lo corre el CI).
- [ ] MFA activo para todos los usuarios del panel.
- [ ] Llaves de Culqi de producción y webhook probados con un cargo real pequeño.
- [ ] Backups de BD activos y una restauración de prueba hecha.
- [ ] Textos legales revisados por un abogado; banco de datos inscrito en la ANPD.
- [ ] Correo `seguridad@codaltoperu.com` creado (ver `SECURITY.md`).
- [ ] Tarifas de envío reales cargadas en el panel (Zonas de envío).
