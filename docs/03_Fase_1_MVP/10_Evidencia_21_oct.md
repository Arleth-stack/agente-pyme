# Evidencia de pruebas de la Fase 1 — 21 de octubre de 2026

Proyecto 2026-544-16 · Agente de WhatsApp para PyMEs · Para el agente mentor y Carlos

Las pruebas se corren contra la base publicada (la misma que usa https://agente-pyme-merkatics.vercel.app), con la llave pública que usa la página, es decir, con los mismos permisos que tiene cualquier visitante o dueño. Los programas de prueba están en el repositorio (carpeta `pruebas/`) y se pueden repetir en cualquier momento.

## 1. Guardado y recuperación (P7, sin éxito falso)

- El formulario guarda el negocio con una sola función de la base (crear_negocio). La pantalla "¡Listo!" solo aparece si la base confirma el guardado; si falla, muestra el error y no se pierde lo escrito.
- Después de crear un negocio, al recargar o volver a entrar con el correo y la contraseña, el panel muestra los mismos datos, horario y preguntas.
- Evidencia real del 21 de octubre: Arleth creó "Tacos El negro" y "Gym Fit" desde la página pública; ambos negocios, con sus preguntas, aparecen en su panel y su chat contesta con esas respuestas.

## 2. Aislamiento entre negocios (P2) — APROBADA, 6 de 6

| Sesión de | Intenta tocar | Leer da 0 | Agregar pregunta rechazado | Cambiar datos: 0 filas | Responder/resolver rechazado | Resultado |
|---|---|---|---|---|---|---|
| Consultorio Dental Sonrisa Clara | Salón Bella | sí | sí | sí | sí | Aprobada |
| Consultorio Dental Sonrisa Clara | Taller Rápido | sí | sí | sí | sí | Aprobada |
| Salón Bella | Consultorio Dental Sonrisa Clara | sí | sí | sí | sí | Aprobada |
| Salón Bella | Taller Rápido | sí | sí | sí | sí | Aprobada |
| Taller Rápido | Consultorio Dental Sonrisa Clara | sí | sí | sí | sí | Aprobada |
| Taller Rápido | Salón Bella | sí | sí | sí | sí | Aprobada |

Sin sesión: no se puede leer ninguna tabla y la función de responder del panel se rechaza. Cada tabla tiene el identificador del negocio y reglas por fila en la base. Cada dueño puede repetir la prueba desde la pestaña "Prueba de aislamiento" de su panel.

## 3. Respuestas del chat (P1) — 107 de 108, 0 inventadas

| Tipo | Aprobadas |
|---|---|
| Pregunta exacta | 36 de 36 |
| Otra forma de preguntar | 35 de 36 |
| Saludo | 6 de 6 |
| No la sabe (debe avisar) | 9 de 9 |
| Pregunta de otro negocio (debe avisar) | 6 de 6 |
| Pide una persona | 3 de 3 |
| Pide cita | 3 de 3 |
| Queja | 3 de 3 |
| ¿Están abiertos? | 6 de 6 |

La única que no coincide («¿cortan cabello de hombre?») contesta los precios de corte, que incluyen el de caballero; no inventa nada.

## 4. Escalamiento a una persona (P4)

| Cliente escribe | El chat contesta | En el panel |
|---|---|---|
| ¿qué servicios tienen? | Menú con las preguntas que sí sabe | — |
| 2 | La respuesta de la opción 2 | — |
| ¿hacen implantes? | "Esa no la tengo a la mano, pero ya le pasé tu pregunta al equipo…" y 3 opciones | Aviso "No la sabe" con el mensaje del cliente |
| ¿qué precios tienen? | Lista de precios escritos por el dueño | El aviso sigue pendiente |
| quiero hacer una cita | Respuesta de citas del negocio | — |
| el sábado a las 11 | "Ya le pasé tu solicitud al equipo…" | El aviso sube a "Pide una cita" |

Desde el panel, el dueño contesta (el mensaje llega al mismo chat) y marca la conversación como resuelta.

## 5. Lenguaje (P5)

0 palabras prohibidas en pantalla.

## Lo que todavía no tiene evidencia

- Validación con una persona real de un negocio de Prioridad 1 (programada para el 27 de octubre).
- Prueba en el celular de otra persona (P9).
