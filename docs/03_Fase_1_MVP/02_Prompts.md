# Prompts del proyecto v2

Proyecto 2026-544-16 · Versión 2.0 · 19 de octubre de 2026

Registro de los prompts que guían la construcción. Sigue las reglas del bootcamp: una tarea por prompt, contexto fijo, criterio visible en pantalla, los cinco elementos (objetivo, contexto, ejemplos, formato y restricciones) y crítica contra un criterio en lugar de "hazlo mejor". Cada prompt real que se use se copia al final, en el registro, con su resultado.

## 1. Prompt de un ticket (3 partes + diseño)

Solo cambia la parte de en medio. Las otras se copian igual cada vez.

**Contexto (fijo):**

> Somos Merkatics. Construimos un módulo multiempresa: el dueño de una PyME crea su negocio con un formulario fácil y rápido y obtiene un chat con aspecto de WhatsApp que contesta solo con sus preguntas frecuentes y le avisa en su panel cuando un cliente necesita a una persona. El mismo sistema atiende a Consultorio Dental Sonrisa Clara, Salón Bella y Taller Rápido, y ninguno puede ver los datos de otro: cada tabla de Supabase lleva negocio_id y reglas por fila; el cliente del chat no lee tablas, solo llama a las funciones chat_*. Pantallas en HTML, CSS y JavaScript con Vite; todos los textos visibles en textos.js. El dueño no es técnico: en pantalla nunca aparecen "IA", "inteligencia artificial", "automatización", "modelo", "bot" ni "entrenar". Ninguna pantalla muestra éxito si la base no lo confirmó. Esta vez no: WhatsApp real, redacción con inteligencia artificial, Django, envío al CRM, cobros ni avisos por correo.

**Pedido:** un solo ticket, el de arriba de la lista. Por ejemplo:

> Ticket T07 — Mis conversaciones: en el panel, la lista de conversaciones del negocio con filtros y conteo (Todas, Te necesitan, Las atiendes tú, Al día). Todavía no hagas el detalle de la conversación ni ningún otro ticket.

**Criterio (cuando esté):** copiado del backlog. Por ejemplo:

> Cuando esté: toco "Te necesitan (2)" y solo quedan esas dos conversaciones; el número coincide con la base.

**Diseño (se pega al final de cada ticket):**

> Construye este ticket aplicando: tipografía con jerarquía y máximo dos familias, espacio generoso entre secciones, alto contraste entre lo importante y el fondo, todo alineado a la misma línea, y que los botones reaccionen al pasar el dedo o el mouse. Pensado primero para celular (desde 360 px), texto de al menos 16 px y botones de al menos 44 px. Sin el estilo genérico de morado con degradado: verde WhatsApp solo en el chat, y un acento sobrio en el panel.

## 2. Crítica de experiencia de usuario (Día 3)

> Actúa como crítico de experiencia de usuario. Evalúa esta pantalla para la dueña de un salón de belleza que la ve por primera vez en su celular. Sé específico en lo que fallaría. Revisa sobre todo que pueda crear su negocio fácil y rápido, sin ayuda, y que ningún texto suene técnico.

Se usa con capturas reales y se aplican dos cambios: uno de flujo y uno de aspecto. El resultado se guarda en 03_Fase_1_MVP/04_Diseño_UX_UI.

## 3. Autocrítica antes de cada entrega

> Actúa como crítico experto en productos multiempresa. Evalúa esta versión contra los criterios de la Fase 1 de la Asignación v2: 3 negocios, formulario fácil y rápido, respuestas solo con la información de cada negocio, aviso a una persona sin inventar, panel por negocio, aislamiento demostrado en la base y cero lenguaje técnico. Sé específico en lo que fallaría.

## 4. Revisión de seguridad (Día 2 y Día 3)

Los cuatro prompts del curso, adaptados al proyecto. Se corren en T18 y se anota qué se cambió.

1. **Base abierta:** "Revisa las reglas por fila de mi base de Supabase. Confirma que una persona sin sesión no puede leer ninguna tabla y que un dueño solo puede leer y escribir filas de su negocio. Dime en español qué cambiaste y cómo compruebo desde afuera que ya no se puede entrar."
2. **Datos de personas:** "Revisa los campos que guardo de dueños y clientes y dime cuáles son datos personales. De cada uno, pregúntame para qué lo necesito, quita los que no se usan y dime cuáles obligan a avisarle a la persona que los estoy guardando."
3. **Validación:** "Valida lo que llega del formulario y del chat antes de guardarlo: los obligatorios no pueden ir vacíos, el correo y el teléfono tienen que tener su forma, y ningún campo puede recibir un texto larguísimo. Si algo está mal, muestra un mensaje claro y no guardes nada."
4. **Llaves en el repositorio:** "Revisa mi proyecto y dime si hay alguna clave, contraseña o token guardado en los archivos. Dime cuáles son públicas a propósito (la llave pública de Supabase) y cuáles no deberían estar ahí, y qué hago con esas."

## 5. Cuando algo truena (Día 2 y Día 3)

> Síntoma en una frase + captura de pantalla. Si no basta: F12 → Console → copiar lo rojo, tal cual, sin traducir.

Si en 10 minutos no sale, se regresa al último commit que funcionaba.

## 6. Registro de prompts usados

| Fecha | Ticket | Prompt (resumen) | Resultado | Ajuste |
|---|---|---|---|---|
| | | | | |
