# Contexto del proyecto (léelo antes de cada ticket)

Proyecto 2026-544-16 · Merkatics GrowthLab · Practicante: Arleth Caballero. Responder siempre en español, sin jerga.

**Qué es:** módulo multiempresa. El dueño de una PyME crea su negocio con un formulario fácil y rápido y obtiene un chat con aspecto de WhatsApp que contesta solo con sus preguntas frecuentes y le avisa en su panel cuando un cliente necesita a una persona. El mismo sistema atiende a Consultorio Dental Sonrisa Clara, Salón Bella y Taller Rápido; ninguno ve los datos de otro.

**Documentos que mandan:** `docs/` (copia del Drive). El orden de trabajo está en `docs/03_Fase_1_MVP/01_Alcance_y_Backlog.md` (tickets T01–T18) y las tablas, reglas y lógica del chat en `docs/03_Fase_1_MVP/05_Modelo_de_Datos.md`.

## Reglas

1. **Un ticket a la vez.** No adelantar tickets. Cada ticket tiene su "Cuando esté": se cumple palabra por palabra.
2. **Terminado = visto en la dirección pública**, guardado en la base y vivo después de recargar. Commit con mensaje claro.
3. **Nunca éxito falso:** ninguna pantalla dice que guardó si la base no lo confirmó.
4. **Aislamiento en la base:** cada tabla lleva `negocio_id` y reglas por fila; el cliente sin sesión no lee tablas, solo llama a las funciones `chat_*`.
5. **Regla de lenguaje:** en pantalla nunca "IA", "inteligencia artificial", "automatización", "modelo", "entrenar", "bot", "prompt", "token", "API" ni "servidor". Textos de pantalla en `src/textos.js` (excepto la página de inicio, cuyo texto fijo vive en `index.html`; la prueba P5 también lo revisa); las respuestas que genera el chat viven en las funciones SQL.
6. **No inventar:** el chat contesta con el texto exacto de la pregunta frecuente del negocio o avisa a una persona. Sin servicios externos de redacción en la Fase 1.
7. **Esta vez no:** WhatsApp real, redacción con inteligencia artificial, Django, envío al CRM, avisos por correo.
8. Gratis y simple: HTML, CSS y JavaScript con Vite; Supabase; Vercel; GitHub.
9. **Cobros (pedido de Carlos, 5 nov 2026):** prueba gratis de 7 días con tarjeta y luego 1 USD al mes, con Stripe en modo de prueba. La tarjeta solo se escribe en la página de Stripe. Las llaves secretas viven en `.env.local` y en Vercel, nunca en git ni en el chat. Funciones en `api/` (`prueba`, `plan`, `portal`, `stripe-aviso`); estado en `negocios.plan_estado` y `plan_termina`. El dueño cambia su tarjeta o cancela en la página de Stripe («Administrar mi plan»). La prueba de aislamiento ya no se muestra en el panel (6 nov, pedido de Arleth); sigue en `pruebas/aislamiento.mjs`.

## Cómo está armado

| Carpeta | Qué hay |
|---|---|
| `index.html`, `chat.html` | Una página por pantalla (Vite multipágina, ver `vite.config.js`) |
| `src/` | JavaScript y estilos; `textos.js` con todos los textos |
| `supabase/migrations/` | Tablas, reglas por fila, funciones y datos de los 3 negocios demo |
| `api/` | Funciones de Vercel para la prueba gratis y el cobro con Stripe |
| `vercel.json` | Rutas limpias: `/chat/salon-bella` → `chat.html` |
| `docs/` | Documentación v2 |

Diseño: celular primero (360 px), texto ≥ 16 px, botones ≥ 44 px. Marca Merkatics (grafito #111111, coral #E95349, letra Jost, logo en `public/marca/`); verde WhatsApp solo en el chat y sus fragmentos. Inicio: `src/inicio.css`; notas de diseño en `.taste-skill/notas.md`.
