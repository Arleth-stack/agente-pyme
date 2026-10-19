# Ficha del proyecto v2

**Proyecto 2026-544-16 · Sistema IA de PYME 2 — Agente de WhatsApp para PyMEs: módulo de entrada multiempresa, integrable a Merkatics**

Merkatics GrowthLab · Generación 11 · Versión 2.0 · 19 de octubre de 2026

Basada en la Asignación de Proyecto, versión 2 (7 de octubre de 2026). Esta versión 2.0 de la documentación acompaña el **reinicio del prototipo desde cero** (ver "Por qué se reinicia").

## Datos generales

| Campo | Contenido |
|---|---|
| Número de proyecto | 2026-544-16 (Carlos debe confirmar: la versión 1 estaba registrada como 2026-544-14) |
| Practicante | Arleth Alejandra Caballero Gutiérrez |
| Carrera | Desarrollo de Software Multimedia |
| Mentor | Carlos (Merkatics) y agente mentor del proyecto |
| Correo / contacto | Pendiente de confirmar |
| Fecha de inicio y entrega (4 meses) | Pendiente de confirmar |
| Origen | Encargo directo de Carlos: subproducto y embudo de adquisición oficial de Merkatics hacia el Growth Operating System |

## Qué es, en una frase

Un **módulo** que muchas PyMEs usan a la vez para que su WhatsApp conteste solo las preguntas frecuentes y avise a una persona cuando hace falta, sin que ningún negocio vea los datos de otro.

## Los tres requisitos de la Fase 1

| Requisito | Qué significa | Cómo se comprueba |
|---|---|---|
| Producto de entrada | Un dueño no técnico lo entiende, lo configura y lo usa sin ayuda. Se vende por el beneficio, nunca por la tecnología | Un negocio nuevo se crea con un formulario en menos de 5 minutos, sin palabras técnicas, y lo prueba una persona real |
| Multiempresa | El mismo sistema atiende a muchos negocios y ninguno ve los datos de otro | Demo con 3 negocios de segmentos distintos, cada uno con su panel, y aislamiento demostrado en la base de datos |
| Integrable a Merkatics | Se diseña desde ahora para conectarse al Growth OS y al CRM | Documento de integración de una página aprobado por Carlos |

## Problema (Need Card)

**Cuando** una PyME sin nadie dedicado a contestar pierde clientes porque no responde WhatsApp a tiempo (de noche, en fin de semana o por volumen), **quiere** que su WhatsApp conteste solo las preguntas frecuentes y le avise cuando un cliente de verdad lo necesita, **para poder** no perder ventas sin tener que aprender nada técnico.

**Señal de éxito:** de cada 10 clientes que escriben, cuántos reciben respuesta en menos de 1 minuto. Meta: 10 de 10.

**Propuesta de valor:** "Tu WhatsApp responde solo, a cualquier hora, y nunca pierdes un cliente por no contestar a tiempo."

## Usuarios

- **Dueño de la PyME:** no técnico, usa el celular, todavía no es cliente de Merkatics, de un segmento de Prioridad 1.
- **Cliente final:** la persona que escribe al WhatsApp del negocio.
- **Merkatics** (comercial y equipo técnico): recibe a esos negocios como prospectos.

## Negocios de la demo (ficticios)

| Negocio | Segmento | Prioridad |
|---|---|---|
| Consultorio Dental Sonrisa Clara | Consultorios y clínicas | 1 — foco inicial |
| Salón Bella | Salones de belleza | 1 — foco inicial |
| Taller Rápido | Talleres mecánicos | 1 |

## Tecnología (Fase 1, todo con plan gratuito)

| Pieza | Herramienta | Para qué |
|---|---|---|
| Pantallas | HTML, CSS y JavaScript con Vite | Inicio, crear negocio, chat, panel y demo |
| Datos y cuentas | Supabase (proyecto nuevo) | Base de datos con identificador de negocio en cada tabla, reglas por fila y cuentas de los dueños |
| Respuestas del chat | Funciones dentro de Supabase | Buscan la respuesta solo entre las preguntas del negocio; si no la encuentran, avisan a una persona |
| Historial | GitHub | Cada cambio queda guardado con su mensaje |
| Publicación | Vercel | Dirección pública que se actualiza sola con cada cambio |
| Canal | Chat web con aspecto de WhatsApp (simulado) | Sustituye a WhatsApp real en la Fase 1 |

En la Fase 1 **no** se usa un servicio externo de redacción de respuestas: el chat contesta con el texto exacto que escribió el dueño. Así es imposible que invente un precio, no hay llaves secretas que proteger y no cuesta nada. Las respuestas redactadas con inteligencia artificial son parte de la Fase 2, como dice la Asignación.

## Fases y fechas

| Fase | Contenido | Cuándo |
|---|---|---|
| Documentación v2 | Este paquete de documentos | 19 oct 2026 |
| Fase 1 — MVP (vibe coding) | Demo de 3 negocios con formulario de alta, chat, aviso a una persona, panel, aislamiento y documento de integración; validado con 1 persona real de Prioridad 1 | 20 al 27 oct 2026 (6 días hábiles) |
| Punto de decisión | Carlos revisa la demo y la evidencia, aprueba la integración y define precio de entrada y gatillo de venta | 28 oct 2026 (propuesto) |
| Fase 2 — Django | Modelo multiempresa real, backend y canal de WhatsApp | Noviembre 2026 |
| Fase 2 — respuestas reales | Respuestas desde las preguntas de cada negocio, aviso real y primera conexión con Merkatics | Fin de nov a inicios de dic 2026 |
| Piloto y Demo Day | Piloto con al menos 1 PyME real | Dic 2026 a inicios de ene 2027 |

## Por qué se reinicia

El primer prototipo mostraba pantallas de éxito sin comprobar que los datos se guardaran, el chat usaba respuestas de ejemplo en lugar de las preguntas de cada negocio, y no estaba demostrado que un negocio no pudiera leer los datos de otro. En lugar de parchar, se reconstruye desde cero con estas reglas:

1. Nada se marca como hecho hasta verlo funcionar en la dirección pública, desde un celular.
2. La pantalla de éxito solo aparece si la base de datos confirmó que guardó.
3. El aislamiento lo garantiza la base de datos, no la pantalla.
4. Un ticket a la vez, con su criterio de "qué se ve" escrito antes de construir.

Los documentos de la versión anterior se conservan en la carpeta 99_Archivo_Version_1 como evidencia de iteración.

## Reglas que no cambian

1. **Puerta de fases:** no se escribe Django antes de que Carlos apruebe la Fase 1 con evidencia real de validación.
2. **Regla de lenguaje:** ningún texto visible para el dueño o el cliente dice "IA", "inteligencia artificial", "automatización", "modelo" ni "entrenar".
3. **Sin inventar:** si la respuesta no está en las preguntas del negocio, avisa a una persona.
4. **WhatsApp real:** no se promete fecha sin confirmar cuánto tarda la verificación de Meta; mientras tanto, canal simulado.
5. **Avances cada dos semanas** con evidencia real (demo funcionando o validación documentada).

## Documentos del proyecto

| Documento | Carpeta |
|---|---|
| Requerimientos (ERS) v2 | 01_Documentacion/02_Requerimientos |
| Problema y usuario v2 | 01_Documentacion/03_Problema_y_Usuario |
| Propuesta de valor y guía de lenguaje v2 | 01_Documentacion/04_Propuesta_de_Valor |
| Registro de decisiones v2 | 01_Documentacion/05_Decisiones_de_Carlos |
| ICP y segmentos v2 | 02_Investigacion_y_Validacion/01_ICP_y_Segmentos |
| Plan de validación v2 | 02_Investigacion_y_Validacion/04_Pruebas_de_Usuario |
| Alcance y backlog de la Fase 1 v2 | 03_Fase_1_MVP/01_Planificacion |
| Prompts del proyecto v2 | 03_Fase_1_MVP/02_Prompts |
| Pantallas y flujo v2 | 03_Fase_1_MVP/04_Diseño_UX_UI |
| Modelo de datos v2 | 03_Fase_1_MVP/05_Base_de_Datos |
| Plan de pruebas v2 | 03_Fase_1_MVP/06_Pruebas |
| Fichas de los 3 negocios v2 | 04_Multiempresa/01 a 03 |
| Cómo se demuestra el aislamiento v2 | 04_Multiempresa/04_Aislamiento_de_Datos |
| Documento de integración con Merkatics v2 | 05_Integracion_Merkatics/01_Documento_de_Integracion |
| Opciones de precio y gatillo de venta v2 | 06_Modelo_de_Negocio/01_Opciones_de_Precio |
