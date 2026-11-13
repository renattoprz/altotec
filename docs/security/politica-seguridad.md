# Política de seguridad de la información

**Alcance:** tienda AltoTec (tec.codaltoperu.com), su código, infraestructura y datos.
**Responsable:** titular de CODALTO (RUC 10704984885).
**Versión:** 1.0 · noviembre 2026.

## Principios

1. **Mínimo dato:** solo se recolecta lo necesario para vender, facturar y enviar.
   Los datos de tarjeta nunca tocan nuestros sistemas (Culqi los tokeniza).
2. **Mínimo privilegio:** cada persona, servicio y credencial tiene solo el acceso
   que necesita. La base de datos no es accesible desde internet.
3. **Defensa en profundidad:** Cloudflare (WAF, límites, Turnstile) → Django
   (CSRF, CSP, validación) → PostgreSQL (usuario con permisos mínimos, cifrado).
4. **Nada de secretos en el código:** las llaves viven en variables cifradas de DigitalOcean;
   el CI busca secretos filtrados en cada cambio.
5. **Todo cambio es revisado:** rama `main` protegida, PR obligatorio, CI en verde.

## Reglas obligatorias

- MFA en todas las cuentas: panel AltoTec, GitHub, DigitalOcean, Cloudflare,
  DigitalOcean, Culqi, correo.
- Contraseñas de 14 caracteres o más, únicas, en un gestor de contraseñas.
- Bloqueo tras 5 intentos fallidos de acceso al panel (1 hora).
- Sesiones del panel de 8 horas como máximo.
- Dependencias revisadas semanalmente (Dependabot) y en cada cambio (pip-audit).
- Respaldo diario cifrado fuera del proveedor de base de datos; prueba de
  restauración mensual documentada.
- Cada cambio de precio, pedido, pago o reclamo queda en el registro de auditoría
  inmutable.
- Los logs no contienen datos personales (filtro automático).
- Acceso de proveedores de equipos: solo información necesaria del pedido,
  bajo acuerdo de confidencialidad.

## Cumplimiento

El incumplimiento de esta política se trata como incidente de seguridad
(ver respuesta-incidentes.md).
