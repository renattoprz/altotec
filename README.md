# AltoTec

Tienda online de equipos para punto de venta (pantallas, ticketeras, lectores,
cajones y kits) de **CODALTO**. Publicada en `tec.codaltoperu.com`.

Especificación funcional aprobada: ver el documento "AltoTec — Especificación de
la tienda online" del proyecto CODALTO.

## Stack

- Django 5.2 LTS (Python 3.13), plantillas del servidor
- PostgreSQL 16, contenedor Docker en DigitalOcean, Cloudflare (WAF, CDN, TLS)
- Pagos: Culqi Online · Comprobantes: AltoFact

## Estructura

| App | Responsabilidad |
| --- | --- |
| `apps/catalog` | Categorías, productos, proveedores y stock confirmado |
| `apps/customers` | Clientes, consentimientos y solicitudes ARCO |
| `apps/orders` | Pedidos, precios en servidor, envíos por zona, pagos y webhook de Culqi |
| `apps/quotes` | Cotizaciones de kits a medida |
| `apps/complaints` | Libro de Reclamaciones virtual |
| `apps/audit` | Registro de auditoría inmutable y filtro de datos personales en logs |

## Desarrollo local

```bash
python3.13 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env              # y pon DJANGO_SECRET_KEY=cualquier-texto-local
python manage.py migrate
python manage.py load_demo_data   # catálogo y zonas de envío ficticios (DEMO)
python manage.py createsuperuser
python manage.py setup_mfa <usuario>   # el panel exige MFA: escanea el QR
python manage.py runserver
```

- Tienda: `http://localhost:8000/` · Panel: `http://localhost:8000/gestion-altotec/`
  (en producción la ruta la define `DJANGO_ADMIN_URL`).
- `manage.py` usa `config.settings.dev` y lee `.env` automáticamente.
- Sin `DB_HOST` usa SQLite. Para usar PostgreSQL como en producción:
  `docker compose up -d db` y en `.env`: `DB_HOST=localhost`,
  `DB_PASSWORD=altotec_local`, `DB_SSLMODE=disable`.
- Sin `CULQI_SECRET_KEY` el pago es **simulado** (botón "Pagar (simulado)").
  Con llaves de prueba de Culqi (`pk_test_…`/`sk_test_…`) se usa el checkout real.
- Los correos se imprimen en la consola.
- Prueba de humo de la imagen de producción: `docker compose --profile app up --build`
  y abrir `http://localhost:8080/`.

## Despliegue

Producción en DigitalOcean detrás de Cloudflare: ver
[docs/deploy-digitalocean.md](docs/deploy-digitalocean.md).

## Calidad y seguridad

```bash
pytest                      # pruebas
ruff check . && ruff format --check .
bandit -r apps config -c pyproject.toml
pip-audit -r requirements.txt
```

El CI (GitHub Actions) corre todo lo anterior, `check --deploy` y gitleaks en cada PR.
Los controles de seguridad y privacidad están en [docs/security](docs/security/README.md).

## Reglas del repositorio

- `main` protegida: todo cambio entra por PR con CI en verde.
- Nunca subir secretos: usar `.env` local (ver `.env.example`) y variables cifradas de DigitalOcean en producción.
- Reportar vulnerabilidades: ver [SECURITY.md](SECURITY.md).
