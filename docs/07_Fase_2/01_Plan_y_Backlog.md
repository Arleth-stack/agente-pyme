# Fase 2: plan y tickets

Proyecto 2026-544-16 · Merkatics GrowthLab · Practicante: Arleth Caballero · Inicio: 17 de noviembre de 2026.

## Qué es la Fase 2

La Fase 1 dejó funcionando el recorrido completo con Supabase (base de datos y funciones SQL) y Vercel. La Fase 2 cambia el motor por uno propio en **Python (Django)** con **MySQL**, y suma lo que la Fase 1 dejó fuera a propósito: **WhatsApp real**, **respuestas redactadas con inteligencia artificial**, **avisos fuera del panel** y **envío al CRM de Merkatics**.

## Decisiones tomadas (17 nov 2026)

| Tema | Decisión | Por qué |
|---|---|---|
| Lenguaje y marco | Python con Django y Django REST Framework | Lo pide la Asignación para la Fase 2; el modelo de datos pasa casi igual |
| Base de datos | MySQL | Pedido de Arleth; PythonAnywhere la incluye gratis |
| Publicación | PythonAnywhere (cuenta gratis) | Gratis, ya trae Django y MySQL, lo más simple |
| Redacción con inteligencia artificial | Opción gratuita: Gemini de Google (capa gratis) | Sin costo; con límites diarios. Si falla o se pasa del límite, el chat contesta con el texto exacto del dueño (como en la Fase 1) |
| WhatsApp | Meta directo (WhatsApp Cloud API) | Gratis para empezar con el número de prueba de Meta |
| Mientras tanto | La versión de la Fase 1 (Vercel + Supabase) sigue publicada hasta que la Fase 2 esté lista y probada | Nunca dejar a nadie sin chat |

## Reglas que siguen igual

1. Un ticket a la vez, con su "Cuando esté" cumplido palabra por palabra.
2. Terminado = visto en la dirección pública, guardado en la base y vivo después de recargar.
3. Nunca éxito falso.
4. Aislamiento: cada consulta del panel filtra por el negocio del usuario; lo comprueba una prueba automática.
5. Regla de lenguaje en pantalla (sin "IA", "bot", "modelo", etc.).
6. **No inventar:** la redacción con inteligencia artificial solo puede reescribir la respuesta que el dueño escribió; si no hay respuesta del dueño, avisa a una persona. Precios, horarios y datos salen siempre del negocio.
7. Llaves secretas solo en `backend/.env` (local) y en el `.env` de PythonAnywhere; nunca en git ni en el chat.

## Tickets

| # | Ticket | Cuando esté |
|---|---|---|
| F2-01 | Proyecto Django + MySQL local | `manage.py check` sin errores; las tablas existen en MySQL; MySQL local arranca con `backend/iniciar_mysql.sh` |
| F2-02 | Modelo multiempresa en Django | Negocio, Miembro (dueño/encargado), Pregunta, Conversación, Mensaje y Aviso con las mismas reglas que en Supabase; prueba automática de aislamiento: una cuenta no puede leer ni cambiar nada de otro negocio |
| F2-03 | Motor del chat en Python | Mismo comportamiento que las funciones SQL de la Fase 1; el conjunto de pruebas `pruebas/conjunto.json` acierta igual o mejor (Fase 1: 107 de 108) |
| F2-04 | API del chat, del panel y de cuentas | El chat público, el alta del negocio, entrar/salir y todo el panel funcionan contra Django; pruebas automáticas de cada dirección |
| F2-05 | Mudanza de datos de Supabase a MySQL | Los 10 negocios, sus preguntas, conversaciones y cuentas pasan a MySQL; los dueños entran con la misma contraseña |
| F2-06 | Pantallas conectadas a Django | Las mismas pantallas (inicio, crear, entrar, panel, chat, demo) usan la API de Django en lugar de Supabase |
| F2-07 | Prueba gratis y cobro en Django | Lo de Stripe (prueba de 7 días, Administrar mi plan, avisos de Stripe) funciona desde Django |
| F2-08 | Redacción con inteligencia artificial (Gemini, gratis) | El chat contesta con naturalidad pero solo con la respuesta del dueño; si Gemini falla o se pasa del límite, usa el texto exacto; el dueño puede apagarla; prueba de "no inventa" |
| F2-09 | WhatsApp real (Meta Cloud API) | Un mensaje al número de prueba de Meta recibe respuesta del chat; el dueño contesta desde el panel y le llega al cliente por WhatsApp |
| F2-10 | Avisos fuera del panel | Cuando un cliente necesita a una persona, al dueño le llega un aviso (correo y/o WhatsApp) |
| F2-11 | Envío al CRM de Merkatics | Cada cita pedida y cada conversación resuelta se registra para el CRM (tabla + CSV descargable); si Merkatics da su API, se envía directo |
| F2-12 | Rol de encargado | El dueño invita a un encargado que solo ve conversaciones y avisos |
| F2-13 | Publicación en PythonAnywhere | Todo vive en `<usuario>.pythonanywhere.com` con MySQL de PythonAnywhere; recorrido completo probado desde un celular |
| F2-14 | Revisión final | Pruebas automáticas en verde, revisión de diseño en 8 anchos, documento de evidencia |

## Avance

| Fecha | Tickets | Evidencia |
|---|---|---|
| 17–18 nov 2026 | F2-01, F2-02, F2-03, F2-04, F2-05 listos en la compu; F2-08, F2-09, F2-10, F2-11 y F2-12 programados y con pruebas, esperando llaves y cuentas | 32 pruebas automáticas en verde (`manage.py test`); conjunto P1 con el motor en Python: 107 de 108, 0 inventadas, y respuesta idéntica a la Fase 1 en los 105 casos comparables (`pruebas/resultados/2026-11-18_P1_python.md`); mudanza: 10 negocios, 10 cuentas (entran con su misma contraseña), 69 preguntas, 26 conversaciones, 89 mensajes, 16 avisos |

Pendiente: F2-06 (pantallas contra Django), F2-07 (Stripe en Django), F2-13 (publicar en PythonAnywhere) y F2-14 (revisión final).

## Lo que necesita Arleth (cuando llegue su ticket)

- **F2-08:** una llave gratis de Gemini en aistudio.google.com (se pega en `backend/.env`, no en el chat).
- **F2-09:** una cuenta de Meta for Developers con una app de WhatsApp (número de prueba).
- **F2-13:** una cuenta gratis en pythonanywhere.com.
