# Propuesta de valor y guía de lenguaje v2

Proyecto 2026-544-16 · Versión 2.0 · 19 de octubre de 2026

## Propuesta de valor

**"Tu WhatsApp responde solo, a cualquier hora, y nunca pierdes un cliente por no contestar a tiempo."**

Se vende por el beneficio, nunca por la tecnología. El dueño compra que sus clientes reciban respuesta y que él se entere cuando lo necesitan; no compra "inteligencia artificial".

| Para el dueño | Beneficio concreto |
|---|---|
| Contesta de noche y en fin de semana | El cliente no se va con la competencia |
| Contesta solo con lo que el negocio escribió | No inventa precios ni promesas |
| Avisa cuando un cliente necesita a una persona | El dueño solo interviene cuando vale la pena |
| Se configura como un formulario en menos de 5 minutos | Sin técnicos ni capacitación |

## Beneficio por segmento de la demo

| Negocio | Lo que más preguntan | Lo que el dueño gana |
|---|---|---|
| Consultorio dental | Precios de limpieza y tratamientos, horario, citas, urgencias | No pierde pacientes que escriben de noche; las urgencias le llegan como aviso |
| Salón de belleza | Precios de cortes, tintes y uñas, horario, citas | Responde precios mientras atiende a otra clienta; las citas le llegan listas para confirmar |
| Taller mecánico | Costo de cambio de aceite o afinación, tiempos, garantía | Contesta cotizaciones básicas sin soltar la herramienta |

## Diferenciación

Ya existen chatbots genéricos de WhatsApp. La diferencia no es el bot: es que **se configura sin jerga en minutos**, **nunca inventa** y es la **puerta de entrada a Merkatics** (seguimiento de clientes y CRM).

## Regla de lenguaje

Ningún texto que vea el dueño o el cliente puede decir **"IA", "inteligencia artificial", "automatización", "modelo" ni "entrenar"**. Cargar preguntas nunca debe sentirse como "entrenar una IA" o escribir instrucciones. La regla aplica a los textos del sistema; lo que el dueño escribe en sus respuestas es suyo (por ejemplo, "modelo 2026" de un producto).

| Evitar | Usar en su lugar |
|---|---|
| IA, inteligencia artificial | "tu WhatsApp", "tu asistente" |
| Automatización, automático, bot | "responde solo", "a cualquier hora" |
| Modelo, entrenar, prompt, base de conocimiento | "tus respuestas", "agrega lo que te preguntan tus clientes" |
| Escalamiento, ticket, alerta | "te necesita un cliente", "necesita tu atención", "aviso" |
| FAQ | "preguntas frecuentes" |
| Tenant, webhook, API, token, base de datos, servidor | No se muestran |
| "Error 500", "fallo de conexión", textos en inglés | "No pudimos guardar. Inténtalo de nuevo en un momento." |

**Cómo se comprueba:** todos los textos visibles viven en un solo archivo del código (textos.js) y una búsqueda automática de las palabras prohibidas debe dar 0.

## Textos de referencia

- **Inicio:** "Tu WhatsApp responde solo, a cualquier hora. Agrega las preguntas que te hacen tus clientes y listo."
- **Formulario:** "¿Cómo lo preguntan tus clientes?" / "¿Qué les respondes?"
- **Bienvenida del chat:** "¡Hola! Soy el asistente de Salón Bella. Te ayudo con precios, horarios y citas. Si prefieres hablar con alguien del equipo, escribe «persona»."
- **Cuando no sabe:** "Esa te la contesta mejor alguien del equipo. Ya le avisé y te escribe en cuanto pueda."
- **Fuera de horario:** "Ya le avisé al equipo. Ahorita estamos cerrados; te escriben mañana a partir de las 10:00 a. m."
- **Aviso al dueño:** "Un cliente te necesita: «¿Hacen extensiones de pestañas?»"
- **Al terminar el formulario:** "¡Listo! Tu WhatsApp de prueba ya contesta. Pruébalo como si fueras tu cliente." (Mientras el canal sea simulado no se dice "Tu WhatsApp ya responde", para no prometer una conexión que todavía no existe.)
- **Resumen del panel:** "Esta semana contestaste a 48 clientes. 10 de 10 tuvieron respuesta en menos de 1 minuto."

El asistente se presenta como "el asistente de [negocio]" y nunca se hace pasar por una persona.
