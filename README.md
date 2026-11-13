# AltoTec

Tienda online de equipos para punto de venta (pantallas, ticketeras, lectores,
cajones y kits) de **CODALTO**. Publicada en `tec.codaltoperu.com`.

Especificación funcional aprobada: ver el documento "AltoTec — Especificación de
la tienda online" del proyecto CODALTO.

## Stack

- Django 5.2 LTS (Python 3.13), plantillas del servidor
- PostgreSQL (Supabase), Google Cloud Run (contenedor), Cloudflare (WAF, CDN, R2)
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
export DJANGO_SECRET_KEY=solo-local
python manage.py migrate
python manage.py createsuperuser
python manage.py setup_mfa <usuario>   # el panel exige MFA
python manage.py runserver
```

Panel en `http://localhost:8000/gestion-altotec/` (en producción la ruta la define
`DJANGO_ADMIN_URL`).

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
- Nunca subir secretos: usar `.env` local (ver `.env.example`) y Secret Manager en producción.
- Reportar vulnerabilidades: ver [SECURITY.md](SECURITY.md).
