# Revisión de entrega (T18): seguridad, lenguaje y experiencia de usuario

Proyecto 2026-544-16 · 20 de octubre de 2026

## 1. Revisión de seguridad (los 4 prompts del curso)

| Revisión | Qué se hizo | Resultado |
|---|---|---|
| Base abierta | Prueba P2 automática: se entra como cada dueño con la llave pública e intenta leer y escribir en los otros negocios; sin sesión se intenta leer cada tabla | 6 de 6 combinaciones aisladas; sin sesión ninguna tabla se lee; las funciones del panel rechazan a quien no es dueño (pruebas/resultados, P2) |
| Datos de personas | Dueños: correo y contraseña (la contraseña la guarda Supabase cifrada). Clientes: los mensajes del chat; nombre y teléfono del cliente solo existen como datos ficticios de la demo. No se guardan datos que no se usen | Con clientes reales (Fase 2) se necesita aviso de privacidad (LFPDPPP) y volver a activar la confirmación por correo |
| Validación | La base valida todo lo que entra: obligatorios, teléfono de 10 dígitos, horario coherente, catálogos, largos máximos (mensaje de 2,000 caracteres rechazado) y crear un negocio exige sesión | Mensajes de error en español en todas las pantallas; nunca un "guardado" falso (P7) |
| Llaves en el repositorio | Búsqueda de llaves y contraseñas en todos los archivos subidos y en todo el historial de GitHub | 0 llaves. La llave pública de Supabase vive en Vercel y en `.env.local`; `.env.local` y `cuentas-demo.local.txt` están fuera de GitHub. La llave secreta solo se usó desde la computadora para crear las cuentas demo |

## 2. Lenguaje (P5)

Búsqueda automática (`node pruebas/lenguaje.mjs`) en 349 textos de pantalla, 6 páginas y 39 frases que contesta el chat: **0 palabras prohibidas**. Se excluyen las preguntas y respuestas que escribe cada negocio (por ejemplo "transmisión automática" del taller), porque la regla aplica a los textos del sistema.

## 3. Crítica de experiencia de usuario (dos cambios aplicados)

Prompt usado: "Actúa como crítico de experiencia de usuario. Evalúa esta pantalla para la dueña de un salón de belleza que la ve por primera vez en su celular. Sé específico en lo que fallaría."

| Lo que fallaría | Cambio aplicado | Tipo |
|---|---|---|
| Quien acaba de crear su negocio llega a un panel vacío que solo dice "Todavía no hay conversaciones" y no sabe qué hacer | El panel vacío explica que comparta el enlace de su chat (estado de WhatsApp, redes, tarjeta), lo muestra y tiene botón "Copiar mi enlace" | Flujo |
| En celular, las pestañas del panel no caben y "Mi negocio" y "Prueba de aislamiento" quedan escondidas a la derecha; "← Volver" se parte en dos líneas | Las pestañas bajan a una segunda línea en pantallas angostas y "← Volver" ya no se parte | Aspecto |

## 4. Pendiente de la entrega

- P9: abrir la dirección pública en el celular de otra persona y hacer una pregunta (lo hace Arleth).
- D3: validación con una persona real de Prioridad 1 (27 de octubre).
- D4: guion de demo de 5 minutos y pitch.
