# Plan de respuesta a incidentes

## Qué es un incidente
Acceso no autorizado, filtración de datos o llaves, cobros indebidos, caída
prolongada, malware, o incumplimiento de la política de seguridad.

## Pasos
1. **Detectar y registrar** (hora 0): anotar qué se vio, cuándo y cómo.
2. **Contener** (primeras 2 h): rotar llaves afectadas (Culqi, BD, Django
   SECRET_KEY), cerrar sesiones, bloquear IPs en Cloudflare, poner la tienda en
   modo mantenimiento si hay riesgo para clientes.
3. **Evaluar**: qué datos y cuántas personas se afectaron (usar el registro de auditoría).
4. **Erradicar y recuperar**: corregir la causa, restaurar desde respaldo si hace falta.
5. **Notificar**:
   - Clientes afectados, en lenguaje claro y sin demora.
   - Autoridad Nacional de Protección de Datos Personales (ANPD) cuando haya
     datos personales comprometidos, según el reglamento vigente de la Ley 29733.
   - Culqi, si involucra pagos.
6. **Aprender** (máx. 5 días después): informe con causa raíz y acciones.

## Contactos
| Rol | Contacto |
| --- | --- |
| Responsable de seguridad | Titular de CODALTO |
| Culqi soporte | Panel de Culqi |
| ANPD | Ministerio de Justicia y Derechos Humanos |
