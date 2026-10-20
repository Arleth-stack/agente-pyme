# Avance de la Fase 1 — 20 de octubre de 2026

Proyecto 2026-544-16 · Agente de WhatsApp para PyMEs · Para revisión de Carlos

## En una frase

Los 18 tickets de la Fase 1 están construidos y comprobados en la dirección pública: un dueño crea su negocio con un formulario fácil y rápido, su WhatsApp de prueba contesta solo con sus preguntas o le avisa en su panel, y los 3 negocios de la demo funcionan con el mismo sistema sin que uno vea los datos de otro. Falta la validación con una persona real (27 de octubre).

## Cómo probarlo

| Qué | Dirección |
|---|---|
| Inicio | https://agente-pyme-merkatics.vercel.app |
| Crear un negocio | https://agente-pyme-merkatics.vercel.app/crear |
| Chat de un negocio de ejemplo | https://agente-pyme-merkatics.vercel.app/chat/salon-bella |
| Panel del dueño | https://agente-pyme-merkatics.vercel.app/entrar (cuentas de la demo con Arleth) |
| Demo para presentar (chat y panel lado a lado, hora simulada, reiniciar) | https://agente-pyme-merkatics.vercel.app/demo |

## Los requisitos de la Asignación v2

| Requisito | Estado | Evidencia |
|---|---|---|
| Producto de entrada: crear el negocio fácil y rápido, sin jerga | Listo | Formulario de 4 pasos con preguntas sugeridas por giro; horario y ubicación se contestan solos; 0 palabras técnicas en pantalla (P5) |
| Multiempresa: 3 negocios, mismo código, aislamiento demostrado | Listo | Sonrisa Clara, Salón Bella y Taller Rápido; prueba automática 6 de 6 combinaciones aisladas y pantalla "Prueba de aislamiento" en el panel (P2) |
| Chat que contesta solo con su negocio y nunca inventa | Listo | 108 casos de prueba: 97 % de preguntas contestadas bien, 0 respuestas inventadas, preguntas de otros negocios siempre avisan (P1) |
| Aviso a una persona | Listo | No la sabe, pidió una persona, pide una cita, queja o urgencia; el dueño contesta desde el panel y el asistente calla hasta que la marca como resuelta (P4) |
| Panel del dueño | Listo | Conversaciones con filtros, atender y resolver, preguntas frecuentes, mi negocio y prueba de aislamiento |
| Integrable a Merkatics | Propuesta lista | Documento de integración v2; campos para el CRM y lugar para la organización de Merkatics ya en la base |
| Validación con persona real | Pendiente | Plan listo; fecha objetivo 27 de octubre |

## Tickets

T01 a T18 terminados del 19 al 20 de octubre, cada uno con su commit en GitHub (repositorio privado Arleth-stack/agente-pyme). Detalle en "Alcance y backlog de la Fase 1 v2".

## Pruebas

| Prueba | Resultado |
|---|---|
| P1 conjunto de prueba (108 casos) | 106 de 108; 0 inventadas |
| P2 aislamiento | 6 de 6; sin sesión no se lee ninguna tabla |
| P3 alta fácil y rápida | Aprobada |
| P4 recorrido del aviso | 6 de 6 pasos |
| P5 lenguaje | 0 palabras prohibidas |
| P6 celular y escritorio | Aprobada |
| P7 sin éxito falso | Aprobada |
| P8 datos inválidos | Aprobada |
| P9 celular ajeno | Pendiente (Arleth) |
| P10 reinicio de la demo | Aprobada |

## Decisiones tomadas durante la construcción

1. El chat contesta con el texto exacto que escribió el dueño (búsqueda dentro de la base); no usa redacción con inteligencia artificial en la Fase 1. Así no puede inventar y no cuesta nada.
2. "Menos de 5 minutos" se entiende como "fácil y rápido": no se cronometra.
3. Las cuentas nuevas no piden confirmar el correo (para la demo); con clientes reales se activa.
4. Los avisos llegan solo al panel; el aviso por correo o WhatsApp es de la Fase 2.

## Lo que falta y quién

| Pendiente | Quién |
|---|---|
| Validación con 1 persona real de Prioridad 1 (D3) | Arleth (Carlos propone el contacto) |
| Abrir la demo en el celular de otra persona (P9) | Arleth |
| Guion de demo de 5 minutos y pitch (D4) | Arleth |
| Aprobar integración (D1), decidir precio de entrada y gatillo de venta (D2) | Carlos |

## Preguntas para Carlos

1. ¿Aprobamos el criterio de la Fase 1 con esta demo y fijamos la revisión el 28 de octubre?
2. ¿Tiene contacto de un dueño de consultorio o salón para la validación?
3. ¿Está bien que en la Fase 1 el chat conteste sin redacción con inteligencia artificial?
4. ¿Las cuentas (Supabase, Vercel) se quedan así para la demo o pasan a Merkatics?
5. ¿Qué datos quiere el CRM y quién del equipo técnico revisa la integración?
6. Relación con Recepción IA (2026-544-26), precio de entrada y gatillo de venta.
