# Modelo de amenazas (STRIDE) — flujo de compra

Activos: dinero de los clientes, datos personales, integridad de precios y pedidos,
reputación de CODALTO, disponibilidad de la tienda.

| Amenaza | Ejemplo | Mitigación |
| --- | --- | --- |
| **S**uplantación | Robo de la contraseña del panel | MFA obligatorio, bloqueo por intentos, URL no estándar |
| **S**uplantación | Webhook falso que marca un pedido como pagado | Token secreto + reconsulta del cargo en la API de Culqi |
| **T**amper (manipulación) | Cliente cambia el precio en el navegador | Precios recalculados desde la BD |
| **T**amper | Cobro por un monto distinto al del pedido | Comparación exacta de montos en el webhook |
| **R**epudio | "Yo no cambié ese precio" | Registro de auditoría inmutable con usuario e IP |
| **I**nformation disclosure | Fuga de datos de clientes por logs | Filtro de datos personales en logs |
| **I**nformation disclosure | Acceso a pedido ajeno por URL | Seguimiento con token aleatorio de 256 bits, no con ID secuencial |
| **I**nformation disclosure | Robo de cookies entre subdominios | Cookies `__Host-`, HttpOnly, Secure, SameSite |
| **D**enegación de servicio | Bots en formularios o checkout | Cloudflare WAF, rate limiting, Turnstile, límite de tamaño de petición |
| **E**levación de privilegios | XSS para robar sesión del admin | Escape automático de plantillas, CSP estricta, HttpOnly |
| **E**levación de privilegios | Inyección SQL | ORM de Django con consultas parametrizadas; Bandit en CI |

Riesgos residuales en registro-riesgos.md.
