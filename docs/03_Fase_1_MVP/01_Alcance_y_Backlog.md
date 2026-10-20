# Alcance y backlog de la Fase 1 v2

Proyecto 2026-544-16 · Versión 2.0 · 19 de octubre de 2026 · Formato del bootcamp de vibe coding (Día 2: Decidir)

Numeración nueva de tickets: los T01 a T15 de la versión 1 quedan en el archivo y no se reutilizan.

## 1. La frase de donde sale todo

**Cuando** un cliente escribe por WhatsApp y no alcanzo a contestar a tiempo, **quiero** que mi WhatsApp conteste solo lo que siempre me preguntan y me avise cuando un cliente me necesita, **para poder** no perder esa venta sin aprender nada técnico.

## 2. Todo lo que el sistema podría hacer (lista cruda)

Un verbo por renglón, sin filtrar:

1. Crear un negocio con un formulario
2. Sugerir preguntas frecuentes según el giro
3. Crear la cuenta del dueño
4. Contestar en el chat con las preguntas del negocio
5. Decir si el negocio está abierto o cerrado
6. Avisar al dueño cuando no sabe la respuesta
7. Avisar al dueño cuando el cliente pide una persona, una cita o tiene una queja
8. Entrar al panel con correo y contraseña
9. Ver las conversaciones con filtro y conteo
10. Contestar al cliente desde el panel
11. Pausar al asistente mientras el dueño atiende y devolvérselo al resolver
12. Agregar, editar, pausar y quitar preguntas
13. Cambiar los datos y el horario del negocio
14. Atender 3 negocios con el mismo sistema
15. Impedir que un negocio vea los datos de otro (en la base)
16. Mostrar en pantalla la prueba de aislamiento
17. Cambiar de negocio, de vista y de hora en la demo, y reiniciarla
18. Guardar nombre, teléfono, interés y resumen para el CRM
19. Mostrar la señal de éxito (clientes con respuesta en menos de 1 minuto)
20. Recuperar la contraseña
21. Redactar respuestas con inteligencia artificial
22. Conectar WhatsApp real
23. Mandar contactos al CRM de Merkatics
24. Avisar al dueño por correo o WhatsApp
25. Roles de encargado
26. Cobros y planes
27. Analítica de preguntas e intención de compra

## 3. MoSCoW

| Debe | Debería | Podría | Esta vez no |
|---|---|---|---|
| 1, 3, 4, 6, 7 — alta del negocio y chat que contesta solo con lo suyo o avisa | 2 — preguntas sugeridas por giro | 19 — señal de éxito en el panel | 21 — redacción con inteligencia artificial (Fase 2) |
| 8, 9, 10, 11 — panel del dueño que atiende avisos | 5 — abierto o cerrado | 20 — recuperar contraseña | 22 — WhatsApp real (Fase 2) |
| 12 — sus preguntas frecuentes | 13 — datos y horario | | 23 — envío al CRM (Fase 2) |
| 14, 15, 16 — multiempresa demostrado | 17 — página de demo | | 24 — avisos externos (Fase 2) |
| | 18 — campos para el CRM | | 25, 26, 27 — roles, cobros y analítica |

La caja "Debe" tiene más de cinco renglones porque la Asignación v2 exige los cuatro bloques (alta, chat, panel y multiempresa). Se agrupan en cuatro para que el paso siga siendo angosto.

## 4. Alcance en un renglón

**Esta vez llega hasta:** un dueño crea su negocio con un formulario, su chat contesta solo con sus preguntas o le avisa en su panel, y tres negocios funcionan con el mismo sistema sin ver los datos de otro.

**Esta vez no:** WhatsApp real (arrastra la verificación de Meta), redacción con inteligencia artificial (arrastra llaves, costo y riesgo de inventar), envío al CRM (arrastra el acceso a Merkatics), avisos por correo o WhatsApp, roles de encargado, cobros y analítica.

## 5. Las cuatro piezas

Cada ticket dice cuáles toca: **Pantalla** (lo que se ve y se toca), **Datos** (lo que se guarda), **Lógica** (lo que pasa al tocarlo) y **Errores** (qué pasa cuando algo sale mal).

## 6. Tickets en orden de construcción

Un ticket es algo que alguien puede ver funcionando. El primero es el **esqueleto que camina**: lo más delgado que atraviesa el sistema de lado a lado.

| # | Ticket | Cuando esté (lo que se ve) | Piezas |
|---|---|---|---|
| T01 | Esqueleto que camina | Abro la dirección pública /chat/salon-bella en mi celular, veo "Salón Bella" (leído de la base), escribo "hola", mi mensaje aparece y sigue ahí después de recargar | Pantalla, Datos |
| T02 | Contesta con las preguntas del negocio | En Salón Bella escribo "cuanto cuesta un corte" (sin acentos) y contesta el precio exacto que escribió el salón | Lógica, Datos |
| T03 | No inventa: avisa a una persona | En Salón Bella pregunto "¿cuánto cuesta el cambio de aceite?" y contesta "Esa te la contesta mejor alguien del equipo…"; en la base aparece un aviso "no la sabe" | Lógica, Datos |
| T04 | Persona, cita y queja | "quiero hablar con alguien", "quiero cita el viernes" y "me dejaron mal el tinte" crean cada uno su aviso con su motivo; tres mensajes seguidos sin respuesta crean un solo aviso | Lógica, Datos |
| T05 | Abierto o cerrado | El encabezado del chat dice "Abierto · cierra a las 8:00 p. m." o "Cerrado · abre mañana a las 10:00 a. m."; fuera de horario, el aviso dice cuándo contestan | Pantalla, Lógica |
| T06 | Entrar a mi panel | Con el correo del dueño de Salón Bella entro y veo "Salón Bella"; con datos equivocados dice "Correo o contraseña incorrectos."; las reglas por fila están activas | Pantalla, Datos, Errores |
| T07 | Mis conversaciones | Veo la lista con filtros y conteo: Todas, Te necesitan, Las atiendes tú y Al día; "Te necesitan (2)" deja solo esas dos | Pantalla, Datos |
| T08 | Atender a un cliente | Abro una conversación que me necesita, escribo una respuesta y aparece en el chat del cliente; mientras la atiendo, el asistente no contesta; con "Marcar como resuelta" vuelve a contestar solo | Pantalla, Lógica, Datos |
| T09 | Mis preguntas frecuentes | Agrego "¿Hacen extensiones de pestañas?" con su respuesta y el chat ya la contesta; pausar una hace que deje de contestarla | Pantalla, Datos |
| T10 | Mi negocio | Cambio el horario del domingo a cerrado y el chat lo dice | Pantalla, Datos |
| T11 | Crear mi negocio: datos y horario | Lleno el paso 1 (nombre, giro, teléfono, dirección) y el paso 2 (horario por día); si falta algo me dice qué en español; "Atrás" no borra lo que escribí | Pantalla, Errores |
| T12 | Crear mi negocio: preguntas | Al elegir "Salón de belleza" aparecen sus preguntas sugeridas; solo escribo mis respuestas, quito o agrego | Pantalla, Lógica |
| T13 | Crear mi negocio: cuenta y ¡Listo! | Escribo correo y contraseña, toco Crear, y solo si la base confirmó que guardó veo "¡Listo!" con el enlace de mi chat; si falla, veo qué pasó y no se crea nada a medias; un doble clic no crea dos negocios | Datos, Lógica, Errores |
| T14 | Los 3 negocios de la demo | Sonrisa Clara, Salón Bella y Taller Rápido existen con sus 12 preguntas, su horario, la cuenta de su dueño y 4 conversaciones de ejemplo cada uno | Datos |
| T15 | Prueba de aislamiento | En el panel de Salón Bella, la pantalla "Prueba de aislamiento" intenta leer los otros dos negocios y muestra "0 conversaciones · 0 preguntas"; las pruebas en la base pasan 6 de 6 | Pantalla, Datos |
| T16 | Página de demo | En una sola página elijo negocio, veo el chat y el panel lado a lado, cambio la hora a "cerrado" y reinicio los datos de ejemplo | Pantalla, Lógica |
| T17 | Inicio | La página principal explica el beneficio sin palabras técnicas y lleva a "Crear mi negocio" y "Entrar a mi panel" | Pantalla |
| T18 | Limpieza y entrega | 0 palabras prohibidas; crítica de experiencia de usuario con 2 cambios aplicados; revisión de seguridad hecha; README de 5 líneas; la dirección abre en el celular de otra persona | Todas |

**Por qué este orden:** primero lo que demuestra que guarda de verdad (T01), luego el corazón del producto (contestar o avisar, T02 a T05), luego el panel que recibe esos avisos (T06 a T10), luego el formulario que crea negocios nuevos (T11 a T13) y al final lo que se necesita para presentarlo (T14 a T18). Los 3 negocios de la demo se cargan directamente en la base; el formulario se prueba creando negocios nuevos. La meta de "menos de 5 minutos" de la Asignación es una forma de decir que crear el negocio debe ser fácil y rápido: no se cronometra.

## 7. Entregables que no son código

| # | Entregable | Carpeta del Drive |
|---|---|---|
| D1 | Documento de integración con Merkatics (una página) | 05_Integracion_Merkatics/01_Documento_de_Integracion |
| D2 | 2 o 3 opciones de precio de entrada y de gatillo de venta | 06_Modelo_de_Negocio |
| D3 | Validación con al menos 1 persona real de Prioridad 1 | 02_Investigacion_y_Validacion |
| D4 | Guion de demo de 5 minutos y pitch | 09_Demo_Day/01_Presentacion |

## 8. Definición de terminado (cada ticket)

- Se ve funcionando **en la dirección pública**, no solo en la computadora.
- Cumple su "Cuando esté" palabra por palabra.
- Si guarda algo, se comprobó en la base y sobrevive a recargar la página.
- Sin palabras prohibidas en pantalla.
- Commit en GitHub con mensaje claro.
- Si cambia cómo contesta el chat, se vuelve a correr el conjunto de prueba.

Si algo se rompe y no sale en 10 minutos, se regresa al último commit que funcionaba.

## 9. Plan de días

| Día | Fecha | Tickets |
|---|---|---|
| 1 | Lun 19 oct | Documentación v2 |
| 2 | Mar 20 oct | T01, T02 y T03 |
| 3 | Mié 21 oct | T04, T05 y T06 |
| 4 | Jue 22 oct | T07, T08, T09 y T10 |
| 5 | Vie 23 oct | T11, T12 y T13 |
| 6 | Lun 26 oct | T14, T15, T16 y T17 |
| 7 | Mar 27 oct | T18, D3 (validación) y D4 |
| — | Mié 28 oct | Revisión con Carlos (propuesta) |

La cita para la validación con la persona real (D3) se agenda desde ya, para el 27 de octubre.
