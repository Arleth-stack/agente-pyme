# Especificación de Requisitos de Software (ERS) v2

**Agente de WhatsApp para PyMEs — módulo de entrada multiempresa, integrable a Merkatics**

Proyecto 2026-544-16 · Estructura basada en IEEE Std 830-1998 · Versión 2.0 · 19 de octubre de 2026

| Campo | Valor |
|---|---|
| Organización | Merkatics GrowthLab · Generación 11 |
| Autora | Arleth Alejandra Caballero Gutiérrez — Desarrollo de Software Multimedia |
| Revisa y aprueba | Carlos (mentor) / Coordinador |
| Documento fuente | Asignación de Proyecto, versión 2 (7 oct 2026) |
| Estado | Borrador para revisión |

Esta versión reemplaza a la ERS 1.0 por el reinicio del prototipo. Cambios principales: el chat contesta con funciones dentro de la base de datos y sin servicio externo de redacción; se agregan requisitos para que ninguna pantalla muestre éxito sin que la base lo confirme. Es un documento interno: la regla de lenguaje aplica a los textos del producto, no a este documento.

# 1. Introducción

## 1.1 Propósito

Definir qué debe hacer el módulo y cómo se comprueba cada requisito, para acordar con Carlos el alcance de la Fase 1 (MVP con vibe coding) y de la Fase 2 (Django multiempresa), y para guiar la construcción y las pruebas.

## 1.2 Alcance

**Producto:** Agente de WhatsApp para PyMEs (nombre interno; el nombre comercial está por definir y no puede incluir "IA").

**Qué es:** un módulo que muchos negocios usan a la vez. Cada dueño crea su negocio con un formulario, escribe sus preguntas frecuentes y obtiene un chat que contesta solo con su información. Cuando no puede resolver, avisa a una persona del negocio en lugar de inventar. Ningún negocio ve los datos de otro, y el diseño permite conectarlo después con el Growth Operating System y el CRM de Merkatics.

**Fuera de alcance de esta estadía:** detección de intención de compra, analítica de preguntas frecuentes, captura avanzada al CRM, cobros, facturación y planes de pago.

## 1.3 Definiciones

| Término | Significado |
|---|---|
| Negocio | Cada PyME que usa el módulo. Todo dato pertenece a un negocio |
| Dueño | Persona que crea el negocio y administra su panel |
| Cliente final | Persona que escribe al chat del negocio |
| Pregunta frecuente | Pregunta y respuesta escritas por el negocio; es la única fuente de las respuestas |
| Aviso | Registro de que una conversación necesita a una persona, con su motivo (en documentos técnicos: escalamiento) |
| Aislamiento | Garantía de que un negocio no puede ver ni modificar datos de otro |
| Reglas por fila (RLS) | Reglas de la base que filtran cada fila según el negocio del usuario |
| Organización de Merkatics | Unidad con la que Merkatics agrupa clientes, con membresías y roles |
| Gatillo de venta | Momento en que se invita al negocio a contratar Merkatics completo |
| Canal simulado | Chat web con aspecto de WhatsApp que sustituye a WhatsApp real en la Fase 1 |

## 1.4 Referencias

1. IEEE Std 830-1998 e ISO/IEC/IEEE 29148.
2. Merkatics GrowthLab, Asignación de Proyecto 2026-544-16, versión 2, 7 oct 2026.
3. Agente mentor del proyecto: análisis de la Asignación v2 y diagnóstico técnico del 19 oct 2026.
4. Bootcamp de Vibe Coding (Días 1 a 3), vibe.fision.org.
5. Documentación de Supabase (Auth y Row Level Security), Vercel y WhatsApp Business Platform.
6. Ley Federal de Protección de Datos Personales en Posesión de los Particulares (LFPDPPP).

## 1.5 Convenciones

Identificadores: RF (funcional), RNF (no funcional), RD (restricción de diseño). Prioridad IEEE 830: **Esencial**, **Condicional** y **Opcional**. Fase: **F1** (MVP) y **F2** (Django). Cada requisito dice con qué ticket se construye (ver Alcance y backlog v2).

# 2. Descripción general

## 2.1 Perspectiva del producto

Es un subproducto y el embudo de adquisición oficial de Merkatics. En la Fase 1 funciona solo, con canal simulado; en la Fase 2 se conecta a WhatsApp real y a Merkatics según el documento de integración aprobado.

| Pieza | Fase 1 | Fase 2 |
|---|---|---|
| Pantallas | HTML, CSS y JavaScript con Vite, publicado en Vercel | Django con plantillas |
| Datos y cuentas | Supabase: identificador de negocio en cada tabla y reglas por fila | Django multiempresa (PostgreSQL) |
| Respuestas | Funciones de la base que buscan solo entre las preguntas del negocio y contestan con el texto exacto del dueño | Redacción con inteligencia artificial, anclada a las preguntas de cada negocio |
| Canal | Chat simulado por negocio | WhatsApp Business (Meta, Twilio o 360dialog) |
| Merkatics | Solo diseño (documento de integración) y campos reservados | Primera conexión con el CRM o su simulación |

## 2.2 Funciones del producto

1. **Alta del negocio:** formulario de 4 pasos con datos, horario y preguntas sugeridas por giro; crea la cuenta del dueño.
2. **Chat del cliente:** contesta con la información de su negocio, dice si está abierto y nunca se hace pasar por persona.
3. **Aviso a una persona:** si no sabe, si el cliente pide una persona o una cita, o si hay queja o urgencia.
4. **Panel del dueño:** conversaciones con filtro y conteo, atender y resolver, preguntas frecuentes y datos del negocio.
5. **Multiempresa:** muchos negocios en el mismo sistema, cada uno aislado en la base.
6. **Demo:** 3 negocios de ejemplo, chat y panel lado a lado, hora simulada, reinicio y prueba de aislamiento.
7. **Integración (diseño):** campos para el CRM y lugar para la organización de Merkatics.

## 2.3 Usuarios

| Usuario | Perfil | Uso | Necesita |
|---|---|---|---|
| Dueño de PyME | No técnico, poco tiempo, usa sobre todo el celular; segmento de Prioridad 1 | Crea su negocio y usa el panel | Configurar como quien llena un formulario y enterarse cuando un cliente lo necesita |
| Cliente final | Usa WhatsApp a diario | Pregunta por el chat | Respuesta rápida y correcta; hablar con alguien si lo necesita |
| Merkatics | Comercial y técnico | Revisa la demo y, en Fase 2, recibe prospectos | Negocios alineados a sus organizaciones y señales de venta |

## 2.4 Restricciones

Puerta de fases, regla de lenguaje, no inventar respuestas, WhatsApp simulado, aislamiento desde el modelo de datos, herramientas gratuitas y Fase 1 en 6 días hábiles (20 al 27 de octubre). Detalle en 3.5.

## 2.5 Suposiciones y dependencias

| ID | Suposición o dependencia | Si no se cumple |
|---|---|---|
| S-01 | Los planes gratuitos de Supabase, Vercel y GitHub alcanzan para la Fase 1 | Se pide a Merkatics cubrir el servicio que se quede corto |
| S-02 | El equipo técnico de Merkatics explica cómo maneja organizaciones, membresías y roles | Se diseña con el supuesto del modelo de datos y se ajusta después |
| S-03 | Carlos confirma 1 o 2 prospectos reales de Prioridad 1 para validar | Se valida con una persona del segmento cercana al equipo y se documenta la limitación |
| S-04 | Carlos define precio de entrada y gatillo de venta antes de aprobar la Fase 2 | La Fase 2 no se aprueba |
| S-05 | El acceso a WhatsApp Business puede tardar | Se sigue con canal simulado |
| S-06 | El plan gratuito de Supabase pausa la base tras una semana sin uso | Se abre la demo antes de cada presentación o se reactiva desde Supabase |

# 3. Requisitos específicos

## 3.1 Interfaces externas

**Interfaces de usuario**

| ID | Pantalla | Descripción | Ticket |
|---|---|---|---|
| UI-01 | Inicio | Explica el beneficio sin jerga; botones "Crear mi negocio" y "Entrar a mi panel" | T17 |
| UI-02 | Crear mi negocio | 4 pasos: Tu negocio, Horario, Preguntas, Tu cuenta; y pantalla ¡Listo! | T11–T13 |
| UI-03 | Chat del negocio | Aspecto de WhatsApp, con nombre del negocio y estado abierto o cerrado | T01–T05 |
| UI-04 | Entrar | Correo y contraseña | T06 |
| UI-05 | Panel del dueño | Conversaciones, detalle, Preguntas frecuentes, Mi negocio y Prueba de aislamiento | T07–T10, T15 |
| UI-06 | Demo | Elegir negocio, chat y panel lado a lado, hora simulada y reiniciar | T16 |

Reglas: diseño pensado primero para celular (desde 360 px), texto de al menos 16 px, botones de al menos 44 px, contraste WCAG 2.1 AA y textos según la guía de lenguaje.

**Interfaces de software**

| ID | Sistema | Uso | Fase |
|---|---|---|---|
| IS-01 | Supabase (PostgreSQL, Auth, reglas por fila y funciones) | Datos, cuentas y lógica del chat | F1 |
| IS-02 | Vercel | Publicar las pantallas | F1 |
| IS-03 | GitHub | Historial de versiones | F1, F2 |
| IS-04 | WhatsApp Business Platform | Canal real | F2 |
| IS-05 | CRM de Merkatics | Recibir contactos y conversaciones | F2 |
| IS-06 | Servicio de redacción con inteligencia artificial | Redactar respuestas ancladas a las preguntas del negocio | F2 |

**Comunicaciones:** HTTPS en todo. El navegador solo usa la llave pública de Supabase; la llave de servicio no aparece en el código ni en GitHub.

## 3.2 Requisitos funcionales

### 3.2.1 Alta del negocio (RF-NEG)

| ID | El sistema debe… | Prioridad | Fase | Ticket | Verificación |
|---|---|---|---|---|---|
| RF-NEG-01 | Permitir crear un negocio con un formulario de 4 pasos: nombre, giro (catálogo), teléfono de 10 dígitos, dirección, horario por día, preguntas frecuentes y cuenta | Esencial | F1 | T11–T13 | Alta completa de un negocio de prueba |
| RF-NEG-02 | Sugerir al menos 5 preguntas típicas del giro elegido, que el dueño contesta, quita o completa | Esencial | F1 | T12 | Al elegir "Salón de belleza" aparecen sus sugerencias |
| RF-NEG-03 | Exigir al menos 3 preguntas con respuesta para terminar | Esencial | F1 | T12 | Intentar terminar con 2 |
| RF-NEG-04 | Crear la cuenta del dueño y su membresía con rol dueño | Esencial | F1 | T13 | Entrar al panel con esa cuenta |
| RF-NEG-05 | Guardar negocio, membresía y preguntas en un solo paso: o se guarda todo o no se guarda nada | Esencial | F1 | T13 | Forzar una falla a la mitad y comprobar que no quedó nada |
| RF-NEG-06 | Mostrar "¡Listo!" solo cuando la base confirmó el guardado, con el enlace del chat y botones "Probar mi chat" e "Ir a mi panel" | Esencial | F1 | T13 | Sin internet al tocar Crear, no aparece ¡Listo! |
| RF-NEG-07 | Validar cada paso con mensajes en español y conservar lo escrito al regresar | Esencial | F1 | T11 | Pasos incompletos y botón Atrás |
| RF-NEG-08 | Evitar negocios duplicados por doble clic | Esencial | F1 | T13 | Doble clic en Crear |

### 3.2.2 Chat del cliente (RF-CHAT)

| ID | El sistema debe… | Prioridad | Fase | Ticket | Verificación |
|---|---|---|---|---|---|
| RF-CHAT-01 | Ofrecer un chat por negocio en /chat/{negocio}, con el nombre leído de la base | Esencial | F1 | T01 | Abrir el chat de cada negocio |
| RF-CHAT-02 | Guardar cada mensaje con negocio, conversación, autor y fecha; la conversación sigue al recargar | Esencial | F1 | T01 | Recargar la página |
| RF-CHAT-03 | Contestar solo con las preguntas frecuentes activas del negocio de ese chat, con el texto exacto del dueño | Esencial | F1 | T02 | Conjunto de prueba: ≥ 90 % correctas |
| RF-CHAT-04 | Reconocer la misma pregunta escrita sin acentos, abreviada o de otra forma | Esencial | F1 | T02 | Cada pregunta del conjunto en 2 formas |
| RF-CHAT-05 | Saludar con el nombre del negocio, decir en qué ayuda y cómo pedir una persona; nunca hacerse pasar por persona | Esencial | F1 | T01 | Primer mensaje de 3 conversaciones |
| RF-CHAT-06 | Mostrar si el negocio está abierto y contestar "¿están abiertos?" según su horario y zona | Esencial | F1 | T05 | Hora simulada abierta y cerrada |
| RF-CHAT-07 | Contestar saludos, gracias y despedidas sin crear aviso | Esencial | F1 | T02 | "hola" y "gracias" no crean avisos |
| RF-CHAT-08 | Mostrar al cliente las respuestas que el dueño escribe desde el panel | Esencial | F1 | T08 | Respuesta visible en el chat en ≤ 5 s |
| RF-CHAT-09 | Si el mensaje no se pudo enviar, decirlo y permitir reintentar sin perder el texto | Esencial | F1 | T01 | Enviar sin internet |

### 3.2.3 Aviso a una persona (RF-AVI)

| ID | El sistema debe… | Prioridad | Fase | Ticket | Verificación |
|---|---|---|---|---|---|
| RF-AVI-01 | Si la respuesta no está en las preguntas del negocio, no inventar y crear aviso "no la sabe" | Esencial | F1 | T03 | 0 respuestas inventadas en el conjunto de prueba |
| RF-AVI-02 | Crear aviso "pidió una persona" cuando el cliente lo pide | Esencial | F1 | T04 | 3 formas de pedirlo |
| RF-AVI-03 | Crear aviso "pide una cita" cuando el cliente pide cita con día u hora | Esencial | F1 | T04 | "Quiero cita el viernes a las 5" |
| RF-AVI-04 | Crear aviso "queja o urgencia" ante queja, dolor o problema | Esencial | F1 | T04 | Casos de queja y de dolor |
| RF-AVI-05 | Decir al cliente que una persona le contestará y cuándo, según el horario | Esencial | F1 | T05 | Caso en horario y fuera de horario |
| RF-AVI-06 | No crear avisos repetidos: un solo aviso pendiente por conversación | Esencial | F1 | T04 | 3 mensajes sin respuesta = 1 aviso |
| RF-AVI-07 | Avisar al dueño fuera del panel (correo o WhatsApp) | Esencial | F2 | — | Aviso recibido en ≤ 60 s |

### 3.2.4 Panel del dueño (RF-PAN)

| ID | El sistema debe… | Prioridad | Fase | Ticket | Verificación |
|---|---|---|---|---|---|
| RF-PAN-01 | Entrar con correo y contraseña y salir; con datos equivocados, mensaje claro | Esencial | F1 | T06 | Flujo de entrada y salida |
| RF-PAN-02 | Mostrar solo el negocio del dueño | Esencial | F1 | T06 | Entrar con cada dueño |
| RF-PAN-03 | Listar conversaciones con filtros y conteo: Todas, Te necesitan, Las atiendes tú, Al día | Esencial | F1 | T07 | El conteo coincide con la base |
| RF-PAN-04 | Mostrar el detalle distinguiendo cliente, asistente y dueño, con el motivo del aviso | Esencial | F1 | T08 | Conversación con los 3 autores |
| RF-PAN-05 | Contestar desde el panel; mientras el dueño atiende, el asistente no contesta | Esencial | F1 | T08 | El asistente calla en "La atiendes tú" |
| RF-PAN-06 | Marcar como resuelta y devolver la conversación al asistente | Esencial | F1 | T08 | Tras resolver, una pregunta cubierta se contesta |
| RF-PAN-07 | Agregar, editar, pausar y quitar preguntas; el cambio se usa en el siguiente mensaje | Esencial | F1 | T09 | Agregar una y preguntarla en el chat |
| RF-PAN-08 | Editar datos y horario del negocio | Condicional | F1 | T10 | Cambiar el horario y preguntarlo |
| RF-PAN-09 | Actualizarse sin recargar cuando llega un mensaje o aviso | Condicional | F1 | T07 | Aparece en ≤ 10 s |
| RF-PAN-10 | Mostrar nombre, teléfono, interés y resumen del cliente (campos para el CRM) | Condicional | F1 | T08 | Visible en el detalle |
| RF-PAN-11 | Mostrar la señal de éxito: clientes con respuesta en menos de 1 minuto | Opcional | F1 | — | Coincide con los datos |

### 3.2.5 Multiempresa (RF-MUL)

| ID | El sistema debe… | Prioridad | Fase | Ticket | Verificación |
|---|---|---|---|---|---|
| RF-MUL-01 | Atender a muchos negocios con el mismo código; cada fila lleva el identificador de su negocio | Esencial | F1 | T01 | Revisión del modelo de datos |
| RF-MUL-02 | Leer y modificar solo datos de los negocios donde el usuario es miembro, con reglas por fila | Esencial | F1 | T06 | Prueba de aislamiento |
| RF-MUL-03 | Impedir que el cliente final lea tablas; solo puede usar las funciones del chat con su token | Esencial | F1 | T01 | Intentar leer tablas sin sesión |
| RF-MUL-04 | Tener 3 negocios de Prioridad 1 (dental, salón, taller) con sus preguntas y conversaciones de ejemplo | Esencial | F1 | T14 | Los 3 existen con datos distintos |
| RF-MUL-05 | Mostrar en pantalla la prueba de aislamiento | Esencial | F1 | T15 | Pantalla con 0 de los otros negocios |
| RF-MUL-06 | Roles por negocio (dueño y encargado) y usuario en varios negocios | Condicional | F2 | — | Pruebas por rol |

### 3.2.6 Demo (RF-DEMO)

| ID | El sistema debe… | Prioridad | Fase | Ticket | Verificación |
|---|---|---|---|---|---|
| RF-DEMO-01 | Página de demo: elegir negocio, chat y panel lado a lado, hora simulada | Esencial | F1 | T16 | Recorrer la demo completa |
| RF-DEMO-02 | Reiniciar las conversaciones de ejemplo de los 3 negocios demo, sin tocar otros negocios | Esencial | F1 | T16 | Reiniciar con un negocio no demo creado |
| RF-DEMO-03 | Cargar conversaciones de ejemplo por negocio para que el panel no se vea vacío | Esencial | F1 | T14 | Cada panel muestra datos al reiniciar |

### 3.2.7 Integración con Merkatics (RF-INT)

| ID | El sistema debe… | Prioridad | Fase | Verificación |
|---|---|---|---|---|
| RF-INT-01 | Guardar por conversación nombre, teléfono, interés y resumen | Condicional | F1 (campos) | Revisión del modelo |
| RF-INT-02 | Tener por negocio un campo para su organización de Merkatics (vacío en F1) | Condicional | F1 | Revisión del modelo |
| RF-INT-03 | Enviar contactos y conversaciones al CRM según el documento aprobado, o simularlo | Esencial | F2 | Registro recibido |
| RF-INT-04 | Exponer la actividad por negocio para el gatillo de venta | Condicional | F2 | Según decisión de Carlos |

## 3.3 Requisitos de rendimiento

| ID | Requisito | Prioridad | Fase |
|---|---|---|---|
| RNF-REN-01 | Respuesta al cliente en ≤ 3 s en el 95 % de los mensajes | Esencial | F1 |
| RNF-REN-02 | Aviso visible en el panel en ≤ 10 s | Esencial | F1 |
| RNF-REN-03 | Soportar al menos 20 negocios con datos de ejemplo sin degradar RNF-REN-01 | Condicional | F1 |

## 3.4 Requisitos lógicos de base de datos

Seis tablas: negocios, miembros, preguntas, conversaciones, mensajes y avisos. Cada una con negocio_id (salvo negocios, que es el propio), reglas por fila activas y catálogos cerrados. El detalle de campos, reglas, funciones y la lógica del chat está en "Modelo de datos v2" (03_Fase_1_MVP/05_Base_de_Datos).

## 3.5 Restricciones de diseño

| ID | Restricción |
|---|---|
| RD-01 | Puerta de fases: nada de Django hasta la aprobación explícita de la Fase 1 con evidencia real de validación |
| RD-02 | La Fase 1 sigue el proceso del bootcamp: idea, prompts, vibe coding, contexto, validación, limpieza, desarrollo y seguimiento; un ticket a la vez |
| RD-03 | Identificador de negocio en cada tabla y reglas por fila desde el primer ticket |
| RD-04 | Negocio, miembros y roles se diseñan para mapearse con organizaciones, membresías y roles de Merkatics |
| RD-05 | Respuestas ancladas: la lógica del chat recibe solo el negocio de la conversación; nunca se mezclan negocios en una consulta |
| RD-06 | WhatsApp simulado en F1; en F2, Meta, Twilio o 360dialog según decisión de Carlos |
| RD-07 | Herramientas gratuitas; si algo cuesta, paga Merkatics. El plan gratuito de Vercel es de uso no comercial: Carlos decide |
| RD-08 | Español de México; zona horaria por negocio |
| RD-09 | Todos los textos visibles en un solo archivo (textos.js) |

## 3.6 Atributos del sistema

| ID | Requisito | Prioridad | Fase | Verificación |
|---|---|---|---|---|
| RNF-LEN-01 | Ningún texto del sistema visible para dueño o cliente dice "IA", "inteligencia artificial", "automatización", "modelo" ni "entrenar" | Esencial | F1, F2 | Búsqueda en textos.js y en las pantallas: 0 |
| RNF-LEN-02 | Evitar también "bot", "prompt", "token", "API", "servidor" y códigos de error | Esencial | F1, F2 | Misma revisión |
| RNF-USA-01 | Un dueño no técnico crea su negocio de forma fácil y rápida (la meta de "menos de 5 minutos" es una forma de decirlo, no se cronometra) y sin ayuda | Esencial | F1 | Prueba con persona real: lo termina sin ayuda |
| RNF-USA-02 | El cliente obtiene horario, precio y ubicación sin instrucciones | Esencial | F1 | Validación |
| RNF-USA-03 | El dueño encuentra y contesta un aviso en 3 toques o menos | Condicional | F1 | Validación |
| RNF-USA-04 | Todo se usa en celular desde 360 px y en escritorio | Esencial | F1 | Revisión en ambos |
| RNF-SEG-01 | El aislamiento lo garantiza la base; con la sesión de A, leer datos de B da 0 y escribir es rechazado | Esencial | F1 | 6 combinaciones |
| RNF-SEG-02 | La llave de servicio no está en el código del navegador ni en GitHub | Esencial | F1 | Revisión del repositorio |
| RNF-SEG-03 | Contraseñas gestionadas por Supabase Auth (mínimo 8 caracteres); HTTPS en todo | Esencial | F1 | Revisión de configuración |
| RNF-SEG-04 | Lo que llega de formularios y chat se valida antes de guardar: obligatorios, formatos y largo máximo | Esencial | F1 | Casos de datos inválidos |
| RNF-FIA-01 | Ninguna pantalla muestra éxito si la base no confirmó; los errores se dicen en español | Esencial | F1 | Pruebas sin internet |
| RNF-FIA-02 | Conjunto de prueba por negocio: ≥ 90 % de cubiertas correctas, 0 inventadas y la pregunta de otro negocio siempre avisa | Esencial | F1 | Resultados en 06_Pruebas |
| RNF-PRI-01 | F1 usa solo datos ficticios; con datos reales (F2) se requiere aviso de privacidad (LFPDPPP) | Esencial | F1, F2 | Revisión |
| RNF-MAN-01 | Código en GitHub con README de 5 líneas; lógica del chat separada de las pantallas | Esencial | F1 | Revisión del repositorio |

# Apéndice A — Criterios de aceptación por fase

**Fase 1 — MVP (Asignación v2)**

- Demo multiempresa con 3 negocios ficticios de segmentos de Prioridad 1 distintos.
- Crear un negocio con el formulario es fácil y rápido (preguntas sugeridas, horario y ubicación que se contestan solos), con sus preguntas, horario y número.
- Chat tipo WhatsApp que contesta solo con la información de su negocio y avisa a una persona cuando no puede.
- Panel del dueño por negocio con conversaciones, preguntas frecuentes y avisos.
- Aislamiento de datos demostrado en la base y en pantalla.
- Sin lenguaje técnico visible.
- Probado por al menos 1 persona real de Prioridad 1, con la validación documentada.
- Documento de integración de una página aprobado por Carlos.
- 2 o 3 opciones de precio de entrada y de gatillo de venta, con ventajas y riesgos.

**Fase 2 — 100 % funcional**

- Desplegado y multiempresa con aislamiento probado.
- WhatsApp real para al menos 1 empresa.
- Respuestas redactadas desde las preguntas configurables de cada negocio.
- Aviso a una persona funcionando de verdad, también fuera del panel.
- Primera conexión con Merkatics según el documento aprobado, o su simulación.
- Piloto con al menos 1 PyME real.

# Apéndice B — Trazabilidad con la Asignación v2

| Lo que pide la Asignación v2 | Requisitos |
|---|---|
| Producto de entrada: formulario fácil y rápido, sin jerga | RF-NEG, RNF-USA-01, RNF-LEN |
| Multiempresa: 3 negocios, mismo código, aislamiento demostrado | RF-MUL-01 a 05, RNF-SEG-01 |
| Integrable: organizaciones, roles y CRM | RF-INT, RD-04 |
| Chat que contesta solo con su negocio | RF-CHAT-01 a 07, RD-05, RNF-FIA-02 |
| Aviso: notificar y registrar, nunca inventar | RF-AVI-01 a 06 |
| Panel del dueño de negocio, no técnico | RF-PAN-01 a 10 |
| Vistas Cliente y Dueño, horario abierto o cerrado, chat y reinicio | RF-DEMO, RF-CHAT-06 |
| Validación con persona real de Prioridad 1 | Apéndice A |
| WhatsApp real sin fecha comprometida | RD-06 |

# Apéndice C — Decisiones pendientes

Ver "Registro de decisiones v2" (01_Documentacion/05_Decisiones_de_Carlos).
