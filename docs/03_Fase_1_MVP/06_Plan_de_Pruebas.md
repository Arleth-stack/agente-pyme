# Plan de pruebas v2

Proyecto 2026-544-16 · Versión 2.0 · 19 de octubre de 2026

Regla del bootcamp: una prueba se marca como aprobada solo cuando se **observó** el resultado, en la **dirección pública** y no en la vista previa. Que la pantalla se vea bien no cuenta. Cada resultado se guarda con fecha y evidencia (captura o tabla) en esta carpeta.

## Pruebas

| # | Prueba | Cómo se hace | Aprobada si… | Tickets |
|---|---|---|---|---|
| P1 | Conjunto de prueba por negocio | Se mandan al chat de cada negocio sus preguntas frecuentes en 2 formas (como la escribió el dueño y sin acentos o abreviada), sus casos de aviso y 2 preguntas de los otros negocios | ≥ 90 % de las preguntas cubiertas contestadas con la respuesta correcta, 0 respuestas inventadas, todos los avisos con su motivo correcto y las preguntas de otros negocios siempre avisan | T02–T05 |
| P2 | Aislamiento en la base | En el editor SQL de Supabase, con la sesión de cada dueño, se intenta leer y escribir en los otros negocios; sin sesión, se intenta leer cada tabla | 6 de 6 combinaciones: leer da 0, escribir es rechazado; sin sesión no se lee nada | T06, T15 |
| P3 | Alta cronometrada | Se crean los 3 negocios de la demo con el formulario, con cronómetro; después, la persona real de la validación crea el suyo | Cada alta en menos de 5 minutos | T11–T14 |
| P4 | Recorrido del aviso | Cliente pregunta algo no cubierto → aparece el aviso en el panel → el dueño contesta → el cliente ve la respuesta → el asistente calla → el dueño resuelve → el asistente vuelve a contestar | Los 6 pasos en la dirección pública, en dos dispositivos | T03, T07, T08 |
| P5 | Lenguaje | Búsqueda automática de las palabras prohibidas en textos.js y en el texto de cada pantalla | 0 apariciones | T18 |
| P6 | Celular y escritorio | Cada pantalla a 360 px y en escritorio | Nada se sale de la pantalla ni se mueve de lado; botones fáciles de tocar | T18 |
| P7 | Sin éxito falso | Se apaga el internet al tocar Crear, al enviar un mensaje y al contestar desde el panel | Ninguna pantalla dice que guardó; el mensaje de error es claro y se puede reintentar sin perder lo escrito | T01, T13 |
| P8 | Datos inválidos | Formulario con campos vacíos, teléfono de 9 dígitos, horario al revés, correo repetido y textos de 2,000 caracteres | Mensaje claro y nada guardado | T11, T13 |
| P9 | Celular ajeno | Alguien de fuera abre la dirección pública en su teléfono y hace una pregunta | Contesta igual que en mi computadora | T18 |
| P10 | Reinicio de la demo | Se crea un negocio que no es demo, se reinicia la demo | Los 3 negocios demo vuelven a sus conversaciones de ejemplo y el otro negocio no se toca | T16 |

## Conjunto de prueba (P1)

Sale de las fichas de los 3 negocios (04_Multiempresa). Por negocio:

| Tipo | Cuántos | Ejemplo (Salón Bella) | Esperado |
|---|---|---|---|
| Pregunta frecuente, forma del dueño | 12 | "¿Cuánto cuesta un corte?" | Respuesta exacta del salón |
| Pregunta frecuente, otra forma | 12 | "cuanto el corte de dama" | Misma respuesta |
| No la sabe | 3 | "¿Hacen extensiones de pestañas?" | Aviso "no la sabe", sin inventar |
| Pide una persona | 1 | "quiero hablar con alguien" | Aviso "pidió una persona" |
| Pide una cita | 1 | "quiero cita el viernes para corte y tinte" | Aviso "pide una cita" |
| Queja o urgencia | 1 | "me dejaron mal el tinte, estoy muy molesta" | Aviso "queja o urgencia" |
| De otro negocio | 2 | "¿cuánto cuesta el cambio de aceite?" | Aviso "no la sabe"; nunca contesta con datos del taller |
| Saludo y gracias | 2 | "hola", "gracias" | Respuesta corta, sin aviso |
| ¿Están abiertos? | 2 | Con hora 10:00 a. m. y 11:00 p. m. | Abierto o cerrado según su horario |

Total: 36 casos por negocio, 108 en total. Los mensajes exactos de "otra forma" se escriben en T02 antes de ajustar la búsqueda, para no acomodarlos al resultado.

## Registro de resultados

| Fecha | Prueba | Resultado | Evidencia | Qué se ajustó |
|---|---|---|---|---|
| | | | | |
