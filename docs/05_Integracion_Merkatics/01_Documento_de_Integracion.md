# Documento de integración con Merkatics v2

Proyecto 2026-544-16 · Propuesta 2.0 · 19 de octubre de 2026 · **Para revisión de Carlos y del equipo técnico de Merkatics.** En la Fase 1 no se programa la integración: se diseña para que sea posible y se dejan los campos reservados.

## 1. Cómo se mapea un negocio con Merkatics

| En el módulo | En Merkatics (a confirmar con el equipo técnico) | Regla |
|---|---|---|
| Negocio | Organización | 1 negocio = 1 organización. El negocio guarda merkatics_org_id (vacío hasta conectarlo) |
| Miembro con rol "dueño" | Membresía con rol de administrador | Se crea al conectar |
| Miembro con rol "encargado" (Fase 2) | Membresía con rol de usuario | Solo ve conversaciones y avisos |
| Cliente de una conversación | Contacto del CRM de esa organización | Se identifica por teléfono; si ya existe, se actualiza |
| Conversación y aviso | Actividad o tarea de seguimiento del contacto | Una por conversación |

## 2. Qué datos pasan al CRM

| Dato | De dónde sale | Ejemplo |
|---|---|---|
| Nombre del contacto | Perfil de WhatsApp (en la Fase 1, dato ficticio) | Mariana López |
| Teléfono | Número de WhatsApp del cliente | 55 0000 2004 |
| Organización | negocio → merkatics_org_id | Salón Bella |
| Interés | Catálogo: precio, cita, servicio, ubicación, queja, otro (según el tema de la pregunta usada o el motivo del aviso) | cita |
| Resumen | 1 o 2 frases de la conversación | "Pidió cita el sábado para peinado y maquillaje" |
| Atención | Si la resolvió el asistente o necesitó a una persona, y el motivo | necesitó persona · pide una cita |
| Fechas | Primer y último mensaje | 19/10/2026 17:40 · 17:52 |
| Origen | Fijo | Agente de WhatsApp |

No se envían los mensajes completos, solo el resumen (menos datos personales y menos costo).

## 3. Cuándo se envían

1. Cuando se crea un aviso de "pide una cita" (es un prospecto caliente).
2. Cuando una conversación se marca como resuelta, o tras 24 horas sin mensajes.

## 4. Cómo se envían (Fase 2)

- **Opción principal:** el módulo llama a la API del CRM de Merkatics (o recibe un webhook), con la organización y los datos de la tabla 2.
- **Si no hay acceso a tiempo:** simulación con una tabla "envíos al CRM" y un archivo CSV que el equipo de Merkatics puede importar.

## 5. Gatillo de venta propuesto

Recomendación (detalle y alternativas en 06_Modelo_de_Negocio): ofrecer Merkatics completo **cuando el dueño necesita algo que solo Merkatics hace** (dar seguimiento a los clientes que preguntaron, recordatorios de cita, campañas), más una **revisión humana a los 30 días** de los negocios más activos. El número de conversaciones y de citas pedidas al mes sirve como señal para el vendedor.

## 6. Privacidad

Con clientes reales, el negocio necesita un aviso de privacidad (LFPDPPP) que diga que sus datos de contacto se comparten con Merkatics para dar seguimiento. En la Fase 1 todos los datos son ficticios.

## 7. Preguntas para el equipo técnico de Merkatics

1. ¿Cómo se llaman y cómo se relacionan organización, membresía y rol en el Growth OS?
2. ¿El CRM tiene API o webhooks? ¿Qué campos obligatorios tiene un contacto?
3. ¿Cómo se identifica a un contacto repetido (por teléfono, por correo)?
4. ¿El módulo será parte del plan estándar o un complemento?
5. ¿Qué relación tiene con Recepción IA (2026-544-26)?

**Aprobación:** [ ] Carlos · [ ] Equipo técnico de Merkatics
