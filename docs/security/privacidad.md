# Privacidad y datos personales

## Inventario
| Dato | Dónde | Finalidad | Base legal | Retención |
| --- | --- | --- | --- | --- |
| Nombre, DNI/RUC | `customers.Customer` | Comprobante y entrega | Ejecución del contrato | 5 años (obligación tributaria) |
| Correo, teléfono | `customers.Customer` | Avisos del pedido | Ejecución del contrato | 5 años |
| Dirección, ubigeo | `orders.Order` | Envío | Ejecución del contrato | 5 años |
| Consentimientos | `customers.Consent` | Prueba de consentimiento | Obligación legal | Mientras exista el cliente + 5 años |
| Datos de cotización | `quotes.Quote` | Preparar la propuesta | Consentimiento | 12 meses si no se cierra |
| Reclamos | `complaints.Complaint` | Libro de Reclamaciones | Obligación legal | Plazo que fije la norma vigente (por verificar) |
| Publicidad | `Customer.marketing_consent` | Ofertas | Consentimiento separado y opcional | Hasta que lo retire |
| Datos de tarjeta | **No se almacenan** (Culqi) | — | — | — |

## Obligaciones
- Inscribir el banco de datos "Clientes" en el Registro Nacional de Protección de
  Datos Personales (ANPD) antes del lanzamiento.
- Política de privacidad publicada y versionada; cada consentimiento guarda la versión.
- Derechos ARCO: formulario dedicado; respuesta dentro de los plazos de ley.
- Encargados del tratamiento: Culqi (pagos), Google Cloud (servidor),
  Supabase (BD), Cloudflare (CDN/archivos), Resend (correo), AltoFact
  (comprobantes). Revisar sus términos de protección de datos.
- Transferencia internacional: los servidores pueden estar fuera del Perú;
  debe informarse en la política de privacidad.
