# Modelo de datos v2

Proyecto 2026-544-16 · Supabase (PostgreSQL) · Versión 2.0 · 19 de octubre de 2026 · Formato del bootcamp (Día 2: Entidad → Campos → Reglas)

## Principios

1. **Cada tabla lleva** negocio_id desde el primer día. No existe un dato que no pertenezca a un negocio.
2. **El aislamiento lo garantiza la base**, con reglas por fila (Row Level Security), no la pantalla.
3. **El cliente final nunca lee tablas.** Su chat solo puede llamar a cuatro funciones que trabajan con el negocio del enlace y con su propia conversación.
4. **Catálogo cerrado en vez de texto libre** para giros, temas, estados y motivos. El único texto libre es lo que escriben las personas.
5. **Pensado para Django y Merkatics:** negocio = organización, miembro = membresía con rol.

## Diagrama

    negocios ─┬─< miembros >── usuarios (cuentas de Supabase)
              ├─< preguntas
              └─< conversaciones ─┬─< mensajes
                                  └─< avisos

## Entidades, campos y reglas

### 1. negocios — cada PyME

| Campo | Regla |
|---|---|
| id | Automático |
| slug | Automático a partir del nombre (minúsculas y guiones); único; es la parte final del enlace del chat: /chat/salon-bella |
| nombre | Obligatorio, de 2 a 60 caracteres |
| giro | Catálogo: consultorio, salon, gimnasio, inmobiliaria, taller, otro |
| telefono | Obligatorio, 10 dígitos |
| direccion | Opcional, hasta 120 caracteres |
| zona_horaria | Catálogo; por defecto America/Mexico_City |
| horario | Obligatorio; por cada día: cerrado, o hora de abrir y de cerrar (cerrar después de abrir) |
| es_demo | Sí o no; solo los 3 negocios de la demo se pueden reiniciar |
| merkatics_org_id | Vacío en la Fase 1; lugar reservado para la organización de Merkatics |
| creado_en | Automático |

### 2. miembros — quién administra cada negocio

| Campo | Regla |
|---|---|
| negocio_id | Obligatorio |
| usuario_id | Obligatorio; la cuenta de Supabase |
| rol | Catálogo: dueno, encargado (encargado se usa hasta la Fase 2) |
| creado_en | Automático |

Un usuario y un negocio forman una sola membresía (no se repite).

### 3. preguntas — las preguntas frecuentes del negocio

| Campo | Regla |
|---|---|
| id | Automático |
| negocio_id | Obligatorio |
| tema | Catálogo: horarios, precios, servicios, citas, pagos, ubicacion, otros |
| pregunta | Obligatoria, hasta 150 caracteres ("¿Cómo lo preguntan tus clientes?") |
| otras_formas | Opcional, hasta 300 caracteres: otras maneras de preguntar lo mismo, separadas por coma |
| respuesta | Obligatoria, hasta 500 caracteres ("¿Qué les respondes?") |
| activa | Sí o no (pausar sin borrar) |
| orden | Número |
| actualizado_en | Automático |

No se permiten dos preguntas iguales en el mismo negocio.

### 4. conversaciones — cada cliente que escribe

| Campo | Regla |
|---|---|
| id | Automático |
| negocio_id | Obligatorio |
| token | Automático y secreto; solo lo conoce el navegador del cliente y le permite ver su conversación |
| cliente_nombre | Opcional (en la Fase 1, ficticio); dato para el CRM |
| cliente_telefono | Opcional, 10 dígitos (en la Fase 1, ficticio); dato para el CRM |
| estado | Catálogo: al_dia, te_necesita, la_atiendes_tu |
| interes | Catálogo: precio, cita, servicio, ubicacion, queja, otro; se llena solo según el tema de la pregunta usada o el motivo del aviso |
| resumen | Opcional, hasta 200 caracteres; lo puede escribir el dueño; dato para el CRM |
| creada_en, ultimo_mensaje_en | Automáticos |

### 5. mensajes — cada mensaje de una conversación

| Campo | Regla |
|---|---|
| id | Automático |
| negocio_id | Obligatorio; siempre igual al de su conversación |
| conversacion_id | Obligatorio |
| autor | Catálogo: cliente, asistente, dueno |
| texto | Obligatorio, de 1 a 1,000 caracteres |
| pregunta_id | Opcional: la pregunta frecuente que se usó para contestar |
| creado_en | Automático |

### 6. avisos — cuando un cliente necesita a una persona

| Campo | Regla |
|---|---|
| id | Automático |
| negocio_id | Obligatorio |
| conversacion_id | Obligatorio |
| motivo | Catálogo: no_la_sabe, pidio_persona, pide_cita, queja_o_urgencia |
| mensaje_cliente | El mensaje que lo provocó |
| estado | Catálogo: pendiente, resuelto |
| creado_en, resuelto_en | Automáticos |

Una conversación solo puede tener **un aviso pendiente** a la vez: si el cliente sigue escribiendo, no se crean avisos repetidos.

## Quién puede hacer qué

| Quién | Cómo entra | Qué puede |
|---|---|---|
| Cliente final (sin cuenta) | Enlace del chat del negocio | Solo llamar a las funciones del chat: ver nombre, horario y estado abierto o cerrado del negocio del enlace, abrir su conversación, mandar mensajes y leer los mensajes de su conversación (con su token). No puede leer ninguna tabla |
| Dueño | Correo y contraseña | Leer y cambiar solo las filas cuyo negocio_id es de un negocio donde es miembro (reglas por fila) |
| Alta de un negocio | Cuenta recién creada | Una sola función crea el negocio, la membresía de dueño y sus preguntas al mismo tiempo; si algo falla, no se guarda nada a medias |
| Demo | Botón Reiniciar | Una función restaura las conversaciones de ejemplo solo de los negocios marcados como demo |

**Llaves:** el navegador solo usa la llave pública de Supabase (está hecha para viajar en la página; lo que protege los datos son las reglas). La llave de servicio no se usa en el código del navegador ni se sube a GitHub.

## Funciones de la base

| Función | Quién la usa | Qué hace |
|---|---|---|
| chat_negocio(slug) | Chat | Regresa nombre, giro, horario y si está abierto ahora; nada más |
| chat_iniciar(slug, nombre, telefono) | Chat | Crea la conversación y regresa su token y la bienvenida |
| chat_enviar(token, texto, hora_simulada) | Chat | Guarda el mensaje, decide la respuesta (ver "Lógica del chat"), guarda la respuesta y, si hace falta, el aviso |
| chat_mensajes(token, desde) | Chat | Regresa los mensajes nuevos de esa conversación (así llegan las respuestas del dueño) |
| crear_negocio(datos) | Formulario | Crea negocio, membresía y preguntas en un solo paso |
| responder(conversacion, texto) | Panel | Guarda el mensaje del dueño y pone la conversación en "la atiendes tú" |
| resolver(conversacion) | Panel | Marca el aviso como resuelto y regresa la conversación a "al día" |
| reiniciar_demo() | Demo | Restaura las conversaciones de ejemplo de los 3 negocios demo |

## Lógica del chat (dentro de chat_enviar)

Siempre trabaja **solo con el negocio de esa conversación**; nunca consulta preguntas de otro negocio.

1. **Limpia el texto:** minúsculas, sin acentos y sin signos ("¿Cuánto cuesta?" y "cuanto cuesta" son iguales).
2. **Si la conversación la atiende el dueño**, guarda el mensaje y no contesta.
3. **Reglas fijas, en este orden:**
   - Queja o urgencia (por ejemplo "me duele", "estoy molesta", "quedó mal", "urgente") → aviso queja_o_urgencia.
   - Pide una persona ("persona", "hablar con alguien", "el doctor", "el encargado") → aviso pidio_persona.
   - Pide una cita con día u hora ("quiero cita el viernes", "me pueden agendar mañana a las 5") → aviso pide_cita. Si solo pregunta cómo funcionan las citas ("¿necesito cita?"), se busca en sus preguntas frecuentes.
   - "¿Están abiertos?" o "¿a qué hora cierran hoy?" → contesta con el horario del negocio y la hora actual.
   - Solo saludo, gracias o despedida → respuesta corta, sin aviso.
4. **Busca la pregunta frecuente más parecida** del negocio, comparando con la pregunta y sus otras formas. Si se parece lo suficiente, contesta con la respuesta **exacta** que escribió el dueño.
5. **Si no se parece a ninguna** → aviso no_la_sabe. Al cliente le dice que una persona le contestará y cuándo, según el horario.

El umbral de parecido se ajusta con el conjunto de prueba (Plan de pruebas): si duda, prefiere avisar a una persona antes que contestar algo equivocado.

## Pruebas de aislamiento

Se ejecutan en el editor SQL de Supabase simulando la sesión de cada dueño:

- Con la sesión del dueño de Salón Bella, contar conversaciones, preguntas y avisos de Taller Rápido → debe dar 0.
- Con esa misma sesión, intentar agregar una pregunta a Taller Rápido → debe ser rechazado.
- Sin sesión (como cliente), intentar leer cualquier tabla → debe dar 0 o ser rechazado.

Se repite para las 6 combinaciones de negocios. Los resultados se guardan en 04_Multiempresa/04_Aislamiento_de_Datos.

## Paso a Django y a Merkatics (Fase 2)

| Supabase (Fase 1) | Django (Fase 2) | Merkatics |
|---|---|---|
| negocios | Empresa | Organización |
| miembros + rol | Usuario y Rol | Membresía y rol |
| preguntas | PreguntaFrecuente | — |
| conversaciones (cliente_nombre, cliente_telefono) | Conversación y Contacto | Contacto del CRM |
| mensajes | Mensaje | Actividad del contacto |
| avisos | Escalamiento | Tarea o seguimiento |
