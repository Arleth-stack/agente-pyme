# Revisión de avances · 23 de noviembre de 2026

## En una frase

La Fase 2 pasa el producto a **Python + Django + MySQL** con **Bootstrap 5**. El "cerebro" del chat ya está en Python y contesta igual que la versión publicada, los datos ya están en MySQL y la base del proyecto ya está acomodada; sigue pasar cada pantalla a Bootstrap.

## Qué está hecho

| Parte | Estado | Cómo se comprueba |
|---|---|---|
| Proyecto Django 6.1 + MySQL | Listo | Corre en la compu (`127.0.0.1:8000`) con su propio MySQL |
| Estructura de carpetas (una app por parte del negocio) | Lista | `backend/`: core, users, inicio, negocios, chat, panel, pagos, canales, crm |
| Diseño: Bootstrap 5 con el tema de Merkatics (grafito, coral, Jost) e iconos Lucide | Listo | Pantalla «Entra a tu panel» |
| Cuentas: el dueño entra con su **WhatsApp** y contraseña | Listo | Salón Bella entra con su número y su misma contraseña de antes |
| Mudanza de datos de Supabase a MySQL | Lista | 10 negocios, 69 preguntas, 26 conversaciones, 89 mensajes, 16 avisos (se ven en `/admin`) |
| Motor del chat en Python | Listo | 108 casos de prueba: 107 correctos, 0 inventados, **idéntico** a la versión publicada |
| Respuestas más naturales con Gemini (gratis) | Listo y probado en vivo | Red de seguridad: si cambia un precio o agrega algo que el dueño no escribió, usa el texto exacto |
| WhatsApp real (Meta), avisos al WhatsApp del dueño, envío al CRM, rol de encargado, cobro con Stripe | Programados con pruebas | Falta conectar la app de Meta y publicar |
| Pruebas automáticas | 38 en verde | `manage.py test` |

## Qué sigue

1. Pasar las pantallas a Bootstrap, una a la vez: inicio → crear negocio → chat → panel → demo.
2. Conectar WhatsApp con la app de Meta (cuenta ya creada).
3. Publicar en PythonAnywhere (`arlethcaballero.pythonanywhere.com`, cuenta ya creada).
4. Revisión final y retirar la versión de Vercel.

## Decisiones de esta etapa

- Django con plantillas + Bootstrap 5 (no React ni Tailwind), como pidió Merkatics.
- El dueño entra con su WhatsApp; los avisos le llegan por WhatsApp, no por correo.
- Inteligencia artificial gratuita (Gemini) con red de seguridad; publicación gratis en PythonAnywhere.
- La versión publicada (Vercel) sigue funcionando mientras se termina la Fase 2.
