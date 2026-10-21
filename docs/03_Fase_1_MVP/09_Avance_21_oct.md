# Avance de la Fase 1 — 21 de octubre de 2026

Proyecto 2026-544-16 · Agente de WhatsApp para PyMEs · Para revisión de Carlos

## En una frase

Después de probarlo con un negocio propio (Tacos El negro), el chat ahora entiende muchas más formas de preguntar, saluda distinto según el giro, sigue contestando después de avisar al dueño y ofrece opciones en vez de dejar al cliente esperando. La página de inicio se rehízo con la marca Merkatics porque es la puerta de entrada, y los demás módulos ya usan la misma marca.

## Qué cambió hoy

### El chat (lo que pidió Arleth tras sus pruebas)

| Antes | Ahora |
|---|---|
| Todos los negocios saludaban igual | La bienvenida cambia según el giro y las preguntas que tiene cada negocio, y muestra botones con sus preguntas para tocar |
| "¿Qué precios tienen?", "¿qué ofrecen?" o "¿qué servicios tienen?" mandaban un aviso | Lista los precios que escribió el dueño, usa su pregunta general si la tiene o muestra un menú con lo que sí sabe contestar |
| "Quiero hacer una cita" sin día mandaba un aviso | Contesta con la pregunta de citas del negocio o pide el día y la hora; "el sábado a las 11" ya avisa como solicitud de cita |
| Sinónimos sin reconocer | Reconoce cita/agendar/reservar, pago/tarjeta/transferencia, horario/abren/días, domicilio/entregas, carro/auto, niño/hijo, hombre/caballero, dental/dientes y más |
| Una sola pregunta por mensaje | "¿Cuánto cuesta la limpieza? ¿y a qué hora abren?" contesta las dos |
| Después del primer aviso contestaba "Ya le avisé" a todo, y cuando el dueño respondía se callaba | Sigue contestando lo que sabe mientras el dueño llega |
| Cuando no sabía solo avisaba | Avisa y además ofrece hasta 3 preguntas relacionadas; el cliente puede tocar una o escribir su número |
| Si faltaba la pregunta de horario o de dirección, avisaba | Contesta con el horario y la dirección que el dueño llenó en el formulario |

Sigue sin redactar: todo lo que contesta es el texto exacto del dueño o una frase fija del sistema.

### El formulario de crear negocio

- Cada pregunta sugerida trae un ejemplo de respuesta en gris (por ejemplo "Corte de dama $250, de caballero $150…"), para que el dueño escriba respuestas completas con precios.
- Si viene de la página de inicio, el nombre y el giro ya llegan escritos.

### Diseño con la marca Merkatics

- Página de inicio nueva: fondo grafito, acento coral, letra Jost (la libre parecida a Futura del logotipo), logo e iconos lineales del manual.
- Portada: el mensaje que llega a las 11:42 p. m. contestado sobre un escenario coral, con el aviso al dueño.
- "Pruébalo como cliente": demo viva dentro de la página. Se elige negocio y hora, y contesta el chat real.
- Secciones: el panel con notas, cómo se empieza, para quién es (con fotos libres acreditadas en el pie), carta de Merkatics, preguntas honestas y un cierre coral que lleva el nombre y el giro al formulario.
- Crear, entrar, panel y demo: barra grafito con el logo, letra Jost, botones coral y avisos en coral. El chat conserva el aspecto de WhatsApp.
- Revisión de diseño automática a 1440, 768 y 390 px: 0 fallas.

## Pruebas del 21 de octubre

| Prueba | Resultado |
|---|---|
| P1 conjunto de prueba (108 casos) | 107 de 108 (antes 106); 0 inventadas. La que falla («cortan cabello de hombre?») contesta los precios de corte, que incluyen el de caballero |
| Conversaciones completas (tacos, consultorio, salón y taller) | Preguntas generales, números, cita en dos mensajes, aviso y seguir contestando: correctas |
| P2 aislamiento | 6 de 6 |
| P5 lenguaje | 0 palabras prohibidas |
| Página pública | Publicada y revisada en https://agente-pyme-merkatics.vercel.app |

## Lo que falta y quién

| Pendiente | Quién |
|---|---|
| Revisar el panel con la cuenta de un negocio demo (cambió solo de colores y letra) | Arleth |
| Corregir las respuestas de Tacos El negro desde su panel (precios completos) | Arleth |
| Abrir la demo en el celular de otra persona (P9) | Arleth |
| Validación con 1 persona real (D3), 27 de octubre | Arleth (Carlos propone el contacto) |
| Aprobar integración, precio de entrada y gatillo de venta | Carlos |
