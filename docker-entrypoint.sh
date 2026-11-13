#!/bin/sh
# Arranque del contenedor. Con RUN_MIGRATIONS=1 aplica migraciones y crea la
# tabla de caché antes de servir (idempotente; seguro en cada despliegue).
set -e
if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
  python manage.py migrate --noinput
  python manage.py createcachetable
fi
exec "$@"
