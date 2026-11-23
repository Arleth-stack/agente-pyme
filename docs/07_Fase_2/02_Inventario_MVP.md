# Inventario del MVP para pasarlo a Django + Bootstrap 5

23 de noviembre de 2026. Lo que hace hoy la versión publicada (Vite + Supabase + funciones de Vercel), pantalla por pantalla, para que Django haga exactamente lo mismo.

## 1. Pantallas y rutas

| Ruta | Pantalla | Qué hace |
|---|---|---|
| `/` | Inicio | Menú lateral (fijo en computadora, «Menú» en celular) con 7 secciones numeradas que se marcan al bajar · portada con chat animado de las 11:42 p. m. · «Pruébalo como cliente»: chat real de los 3 negocios demo, con hora simulada (Ahora / 12:30 p. m. / 11:42 p. m.), pistas y «Abrir el chat completo» · QR del negocio elegido para probar en el celular · «Y te avisa a ti» (panel de ejemplo) · «Así empiezas» · «Para quién es» (preguntas por giro con foto) · Merkatics · Preguntas (acordeón con respuesta grande en computadora) · «Empieza con tu nombre» (nombre + giro → Crear) · pie con créditos de fotos |
| `/crear` | Crea tu negocio | 5 pasos: 1 negocio (nombre, giro, WhatsApp 10 dígitos, dirección) · 2 horario por día (editor, «Usar el horario del lunes de martes a viernes») · 3 preguntas sugeridas por giro (mín. 3 con respuesta, sin repetir, agregar/quitar) · 4 cuenta (correo, contraseña ×2) · 5 «¡Tu chat ya contesta!» con enlace, Copiar, Probar mi chat y la prueba gratis de 7 días con línea de tiempo · llega con `?nombre=&giro=` desde el inicio |
| `/entrar` | Entra a tu panel | Correo y contraseña; si ya hay sesión va al panel; enlace a Crear |
| `/panel` | Panel del dueño | Menú lateral con nombre del negocio, contador «te necesitan» y estado del plan · ver lista abajo |
| `/chat/<negocio>` | Chat del cliente | Aspecto de WhatsApp · bienvenida por giro, abierto/cerrado con hora · burbujas, «escribiendo…», reintento si no se envió · opciones numeradas como botones · revisa mensajes nuevos cada 4 s y el horario cada minuto · recuerda la conversación en el navegador · hora simulada solo en negocios demo |
| `/demo` | Demo para presentar | Selector de negocio y hora · chat del cliente y panel del dueño lado a lado (pestañas en celular) · aviso si el panel es de otro negocio · «Reiniciar demo» (vuelve a cargar las conversaciones de ejemplo) |

## 2. Panel del dueño, sección por sección

| Sección | Funciones |
|---|---|
| Tus primeros pasos | 4 pasos con avance (crear, activar prueba, probar como cliente, compartir); se puede ocultar |
| Conversaciones | Filtros Todas / Te necesitan / Las atiendes tú / Al día con conteo · lista ordenada (urgentes arriba) con motivo · detalle con mensajes, datos del cliente, aviso · contestar (pasa a «La atiendes tú») · marcar como resuelta · «Agregar como pregunta» cuando el chat no supo · se actualiza sola cada 5 s |
| Preguntas frecuentes | Lista por tema · agregar, editar, pausar/activar, quitar (con confirmación) · formulario con «otras formas de preguntarlo» · aviso si está repetida |
| Reportes | Tu semana / Tu mes · tarjetas (conversaciones, resueltas por el chat con %, te necesitaron, respuestas) · barras por día · lo más preguntado · lo que no supo (con «Agregar como pregunta») · por qué te necesitaron |
| Comparte tu chat | Enlace + Copiar · Compartir por WhatsApp con mensaje listo · Probar mi chat · QR para probar o imprimir |
| Mi negocio | Nombre, WhatsApp, dirección y horario; «Listo, guardamos tus cambios» solo si la base confirmó |
| Plan | Prueba gratis de 7 días con tarjeta en Stripe (modo de prueba) · 1 dólar al mes · días que quedan · Administrar mi plan (página de Stripe: tarjeta, cobros, cancelar) · avisos de cancelado, pago pendiente, bienvenida al volver |

## 3. Datos (tablas)

negocios (con plan y Stripe) · miembros (dueño/encargado) · preguntas · conversaciones · mensajes (con opciones ofrecidas) · avisos (un pendiente por conversación, con prioridad) · Datos de ejemplo: 3 negocios demo con 4 conversaciones cada uno, 69 preguntas en total, fotos en `public/fotos`, logos en `public/marca`.

## 4. Permisos

- Cliente del chat: sin cuenta; solo lee y escribe su conversación con su token.
- Dueño: ve y cambia solo su negocio (aislamiento por negocio en cada consulta).
- No puede cambiar su plan ni marcarse como demo.
- Los negocios demo no pagan y aceptan hora simulada.

## 5. Lo que hace el chat (motor)

Contesta con el texto exacto de la pregunta frecuente que mejor coincide (sinónimos, raíces, parecido de palabras, ignora el nombre del negocio) · elegir por número de una lista · varias preguntas en un mensaje · preguntas generales (precios, servicios, citas, horario, ubicación) · menú de lo que sí sabe · horario y dirección desde los datos del negocio · detecta queja/urgencia, pedir persona, pedir cita (también por contexto) · si no sabe, avisa y ofrece 3 opciones · nunca inventa. **Fase 1 no usa inteligencia artificial.**

## 6. Ya hecho en Python (17–23 nov) que se reaprovecha

Motor del chat (idéntico al MVP, 107/108) · mudanza de datos con contraseñas · Stripe · redacción con Gemini y red de seguridad · WhatsApp (Meta) · avisos por correo/WhatsApp · CRM con CSV · rol de encargado · 34 pruebas.
