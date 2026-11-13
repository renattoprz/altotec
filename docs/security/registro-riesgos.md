# Registro de riesgos

Escala 1–5. Riesgo = probabilidad × impacto. Revisión semestral.

| ID | Riesgo | P | I | R | Tratamiento | Responsable |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | Proveedor no entrega tras el cobro (responsabilidad ante Indecopi) | 3 | 4 | 12 | Venta online solo con stock confirmado en 48 h; acuerdo escrito con proveedores; reembolso rápido | Titular |
| R2 | Robo de credenciales del panel | 2 | 5 | 10 | MFA, bloqueo, gestor de contraseñas | Titular |
| R3 | Filtración de llaves de Culqi | 2 | 5 | 10 | Secret Manager, gitleaks, rotación ante sospecha | Titular |
| R4 | Fraude con tarjetas robadas | 3 | 3 | 9 | Antifraude de Culqi, revisión manual de pedidos de alto monto | Titular |
| R5 | Pérdida de base de datos | 1 | 5 | 5 | Respaldo diario externo + prueba mensual | Titular |
| R6 | Dependencia vulnerable | 3 | 3 | 9 | Dependabot + pip-audit en CI | Titular |
| R7 | Caída del proveedor de nube | 2 | 3 | 6 | Contenedor portable (Docker), Postgres estándar, DNS en Cloudflare | Titular |
| R8 | Brecha de datos personales | 1 | 5 | 5 | Minimización, controles de acceso, plan de incidentes y aviso a la ANPD | Titular |
| R9 | Persona clave única (bus factor) | 4 | 4 | 16 | Documentación, accesos de emergencia guardados en sobre sellado / gestor compartido | Titular |
