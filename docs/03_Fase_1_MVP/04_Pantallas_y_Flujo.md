# Pantallas y flujo v2

Proyecto 2026-544-16 · Versión 2.0 · 19 de octubre de 2026

Todo se diseña primero para celular (desde 360 px), con texto de al menos 16 px, botones de al menos 44 px y sin palabras técnicas. Se conserva la idea de la demo anterior: chat con aspecto de WhatsApp, vistas Cliente y Dueño, estado abierto o cerrado y reinicio.

## Mapa de pantallas

| Dirección | Pantalla | Quién la usa | Ticket |
|---|---|---|---|
| / | Inicio | Dueño | T17 |
| /crear | Crear mi negocio (4 pasos) y ¡Listo! | Dueño | T11–T13 |
| /chat/{negocio} | Chat del negocio | Cliente final | T01–T05 |
| /entrar | Entrar a mi panel | Dueño | T06 |
| /panel | Panel del dueño | Dueño | T07–T10, T15 |
| /demo | Demo para presentar | Arleth | T16 |

Recorrido del dueño: Inicio → Crear mi negocio → ¡Listo! → Probar mi chat o Ir a mi panel.
Recorrido del cliente: enlace del negocio → chat.

## P1 · Inicio

- Título: "Tu WhatsApp responde solo, a cualquier hora."
- Texto: "Escribe las preguntas que te hacen tus clientes y te avisamos cuando alguien te necesite."
- Tres beneficios cortos: "Contesta de noche y en fin de semana", "Nunca inventa precios", "Te avisa cuando un cliente te necesita".
- Botones: **Crear mi negocio** y **Entrar a mi panel**.

## P2 · Crear mi negocio (4 pasos, fácil y rápido)

Barra de avance "Paso 1 de 4", botones Atrás y Siguiente. Cada paso valida antes de avanzar y Atrás conserva lo escrito.

| Paso | Campos | Ayuda en pantalla |
|---|---|---|
| 1. Tu negocio | Nombre, giro (Consultorio o clínica, Salón o barbería, Gimnasio o estudio, Inmobiliaria, Taller, Otro), WhatsApp del negocio (10 dígitos), dirección (opcional) | "Así te verán tus clientes" |
| 2. Horario | Por día: abierto o cerrado, hora de abrir y de cerrar; botón "Usar el mismo horario de lunes a viernes" | "Si alguien escribe fuera de horario, le diremos cuándo le contestas" |
| 3. Preguntas | Preguntas sugeridas según el giro, cada una con "¿Qué les respondes?"; botones Quitar y "+ Agregar otra pregunta" | "Escribe la respuesta como se la darías por WhatsApp, con precios y datos exactos" |
| 4. Tu cuenta | Correo, contraseña y repetir contraseña | "Con esto entras a tu panel para ver a tus clientes" |

Mensajes de error (ejemplos): "Escribe el nombre de tu negocio.", "El número debe tener 10 dígitos.", "La hora de cierre debe ser después de la de apertura.", "Contesta al menos 3 preguntas para que tu WhatsApp pueda ayudar.", "Ese correo ya tiene una cuenta. ¿Quieres entrar a tu panel?", "La contraseña debe tener al menos 8 caracteres.", "No pudimos guardar tu negocio. Revisa tu internet e inténtalo de nuevo."

Mientras guarda, el botón dice "Creando tu negocio…" y no se puede volver a tocar.

## P3 · ¡Listo!

Solo aparece cuando la base confirmó que guardó todo.

- "¡Listo! Tu WhatsApp de prueba ya contesta."
- El enlace del chat del negocio, con botón Copiar.
- Botones **Probar mi chat** e **Ir a mi panel**.

## P4 · Chat del negocio

Aspecto de WhatsApp: encabezado verde con iniciales y nombre del negocio, debajo "Abierto · cierra a las 8:00 p. m." o "Cerrado · abre mañana a las 10:00 a. m."; burbujas con hora; caja para escribir y botón enviar.

- El primer mensaje es la bienvenida con el nombre del negocio y cómo pedir una persona.
- Mientras espera respuesta: "escribiendo…".
- Si un mensaje no se pudo enviar: la burbuja se marca con "No se envió · Toca para reintentar".
- Si el enlace no existe: "No encontramos este negocio. Revisa el enlace."
- La conversación sigue ahí al recargar (el navegador recuerda su token).

## P5 · Entrar

Correo, contraseña y **Entrar**. Mensajes: "Correo o contraseña incorrectos." y "No hay conexión. Revisa tu internet."

## P6 · Panel del dueño

Encabezado: nombre del negocio, enlace a su chat y **Salir**. Pestañas abajo en celular y a la izquierda en escritorio.

| Sección | Contenido |
|---|---|
| Conversaciones | Filtros con conteo: Todas, Te necesitan, Las atiendes tú, Al día. Cada fila: cliente, último mensaje, hace cuánto y estado; las que necesitan atención van arriba y resaltadas |
| Detalle | Mensajes con autor ("Cliente", "Respondió tu WhatsApp", "Tú"), el motivo del aviso ("No la sabe", "Pidió una persona", "Pide una cita", "Queja o urgencia"), caja "Escribe tu respuesta", botón **Marcar como resuelta** y datos del cliente (nombre, teléfono, interés, resumen) |
| Preguntas frecuentes | Agrupadas por tema; Agregar, Editar, Pausar y Quitar; mismos campos que el paso 3, más "Otras formas de preguntarlo" |
| Mi negocio | Datos y horario editables |
| Prueba de aislamiento | Ver P7 |

## P7 · Prueba de aislamiento

Con la sesión del dueño que entró, intenta leer los otros negocios de la demo y muestra:

| Negocio | Conversaciones que puedes ver | Preguntas que puedes ver |
|---|---|---|
| Salón Bella (tu negocio) | 4 | 12 |
| Consultorio Dental Sonrisa Clara | 0 | 0 |
| Taller Rápido | 0 | 0 |

Texto: "Cada negocio ve solo su información. Aunque se intente, Salón Bella no puede leer nada de los otros negocios."

## P8 · Demo

Una sola página para presentar:

- Selector de negocio: Sonrisa Clara, Salón Bella, Taller Rápido.
- Chat (izquierda) y panel (derecha) lado a lado en escritorio; en celular, pestañas Cliente y Dueño.
- Hora: "Hora real", "10:00 a. m. (abierto)", "11:00 p. m. (cerrado)".
- Botón **Reiniciar demo** (pide confirmar).

## Flujo de la demo para Carlos (5 minutos)

| Tiempo | Qué se hace | Qué demuestra |
|---|---|---|
| 0:00–0:20 | La frase: "Tu WhatsApp responde solo y nunca pierdes un cliente por no contestar a tiempo" | Propuesta de valor |
| 0:20–1:00 | El problema con números (de la validación real) | Problema real |
| 1:00–2:00 | Crear un negocio en vivo con el formulario (los 3 de ejemplo ya existen) | Producto de entrada: fácil y rápido, sin ayuda |
| 2:00–3:00 | Chat de Salón Bella: precio de un corte (contesta); cambio de aceite (avisa a una persona); cita el viernes (aviso de cita) | Contesta solo con su información y avisa |
| 3:00–3:40 | Panel de Salón Bella: el aviso, contestar, marcar como resuelta | Panel del dueño |
| 3:40–4:20 | Prueba de aislamiento y panel de Taller Rápido sin nada del salón | Multiempresa demostrado |
| 4:20–5:00 | Documento de integración, opciones de precio y la petición a Carlos | Integrable a Merkatics |

Respaldo: capturas del flujo completo en el celular por si falla internet.
