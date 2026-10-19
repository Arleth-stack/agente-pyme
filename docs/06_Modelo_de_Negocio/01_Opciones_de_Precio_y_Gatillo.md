# Opciones de precio de entrada y gatillo de venta v2

Proyecto 2026-544-16 · Propuesta 2.0 · 19 de octubre de 2026 · **Arleth propone; Carlos decide.**

El módulo tiene dos capas de valor (Asignación v2): la **capa 1** es el ingreso directo del módulo y la **capa 2**, la que importa, es que ese cliente pase a Merkatics completo. Sin estas dos decisiones no se aprueba la Fase 2.

## Costo de operación (referencia)

| Concepto | Fase 1 (demo) | Con clientes reales (Fase 2) |
|---|---|---|
| Respuestas del chat | 0: se buscan entre las preguntas del negocio dentro de la base | Si se agrega redacción con inteligencia artificial, un modelo ligero cuesta del orden de unos pocos dólares por cada 1,000 conversaciones (a confirmar con el proveedor elegido) |
| WhatsApp | 0: canal simulado | Con Meta, contestar dentro de las 24 horas a un cliente que escribió primero no tiene costo por mensaje; Twilio o 360dialog cobran su propia tarifa; los mensajes que inicia el negocio sí cuestan |
| Pantallas y base de datos | 0 en planes gratuitos | Con volumen real habría que pasar a planes de pago |

## Capa 1 · Precio de entrada

| Opción | Cómo funciona | Ventajas | Riesgos |
|---|---|---|---|
| A. Gratis con límite | Gratis hasta 100 conversaciones al mes; Merkatics absorbe el costo como costo de adquisición | Cero fricción; máxima adopción; mensaje de venta simple | Merkatics paga por negocios que tal vez nunca conviertan; hay que vigilar el límite |
| B. Freemium | Gratis: preguntas frecuentes, avisos en el panel y hasta 100 conversaciones. Básico (por ejemplo $299 MXN al mes): más conversaciones, avisos al celular del dueño y un encargado | Ingreso desde el inicio para quien usa más; el plan gratis sigue atrayendo | Dos planes que explicar; el plan de pago puede competir con Merkatics completo |
| C. Cargo bajo con prueba | Por ejemplo $199 MXN al mes después de 14 días gratis | Filtra negocios serios; cubre el costo de operación | Menos adopción; un dueño no técnico duda en pagar por algo nuevo |

Los montos son hipótesis para probar en la validación preguntando por el pasado ("¿cuánto pagas hoy por…?"), nunca "¿cuánto pagarías?".

## Capa 2 · Gatillo de venta hacia Merkatics

| Opción | Cuándo se invita | Ventajas | Riesgos |
|---|---|---|---|
| 1. Por volumen | Al pasar, por ejemplo, 100 conversaciones o 20 citas pedidas en un mes: aviso en el panel y al vendedor | Automático y medible | Volumen no siempre es disposición a pagar |
| 2. Por necesidad | Cuando el dueño quiere algo que solo Merkatics hace: seguimiento a quienes preguntaron, recordatorios de cita o campañas. El panel muestra "Tienes 23 clientes que preguntaron precios este mes. Con Merkatics les das seguimiento." | La oferta llega cuando el dueño ya ve el valor | Requiere diseñar esos puntos de entrada en el panel |
| 3. Revisión humana | A los 30 días, un vendedor de Merkatics revisa la actividad y contacta a los negocios más activos | Conversación personal; aprovecha el canal de venta de Merkatics | Depende del tiempo del equipo comercial; no escala solo |

## Recomendación

- **Precio:** opción **A (gratis con límite)** durante el piloto, para medir el uso real sin fricción, y decidir entre B o C con esos datos.
- **Gatillo:** **2 (por necesidad) + 3 (revisión humana)**, usando el volumen (1) solo como señal para el vendedor.

## Decisión de Carlos

| Tema | Opción elegida | Fecha | Comentarios |
|---|---|---|---|
| Precio de entrada | | | |
| ¿Merkatics subsidia el costo de operación? ¿Con qué límite? | | | |
| Gatillo de venta | | | |
| ¿Plan estándar o complemento? | | | |
