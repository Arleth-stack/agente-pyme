# Cómo se demuestra el aislamiento entre negocios v2

Proyecto 2026-544-16 · Versión 2.0 · 19 de octubre de 2026

**Requisito (Asignación v2):** "Ningún negocio puede ver los datos de otro… se demuestra que uno no ve lo del otro." No basta con que los tres negocios se vean distintos en pantalla: ocultar información en la interfaz no es lo mismo que protegerla en la base de datos.

## Tres capas de protección

| Capa | Qué impide | Cómo se comprueba |
|---|---|---|
| 1. Reglas por fila en la base | Que un dueño lea o cambie filas de un negocio donde no es miembro | Prueba en la base (abajo) |
| 2. El cliente no lee tablas | Que alguien con el enlace del chat lea conversaciones o preguntas de cualquier negocio | Sin sesión, leer cualquier tabla da 0 o es rechazado |
| 3. La lógica del chat filtra por negocio | Que el chat de un negocio conteste con información de otro | Preguntas cruzadas del conjunto de prueba: siempre avisan |

## Prueba en la base (6 combinaciones)

Para cada dueño (Sonrisa Clara, Salón Bella, Taller Rápido) y cada uno de los otros dos negocios:

| Intento | Esperado |
|---|---|
| Leer conversaciones del otro negocio | 0 filas |
| Leer preguntas del otro negocio | 0 filas |
| Leer avisos del otro negocio | 0 filas |
| Agregar una pregunta al otro negocio | Rechazado |
| Cambiar el horario del otro negocio | 0 filas cambiadas |

Y sin sesión (como cualquier persona con el enlace): leer negocios, preguntas, conversaciones, mensajes y avisos → nada.

## Prueba en pantalla (para la demo)

En el panel, la sección "Prueba de aislamiento" usa la sesión del dueño que entró para intentar leer los otros dos negocios y muestra la tabla con sus conteos: el propio negocio con sus números reales y los otros con 0. Se presenta en vivo en la demo, entrando primero como Salón Bella y después como Taller Rápido.

## Prueba en el chat

Del conjunto de prueba: en cada negocio se preguntan 2 cosas que solo sabe otro negocio (por ejemplo, en Salón Bella "¿cuánto cuesta el cambio de aceite?"). Resultado esperado: aviso "no la sabe", nunca la respuesta del otro negocio.

## Registro de resultados

| Fecha | Prueba | Combinaciones aprobadas | Evidencia |
|---|---|---|---|
| | Base | de 6 | |
| | Sin sesión | de 5 tablas | |
| | Pantalla | de 3 negocios | |
| | Chat (preguntas cruzadas) | de 6 | |
