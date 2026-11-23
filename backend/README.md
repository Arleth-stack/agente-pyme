# Tu WhatsApp contesta solo · Django

Python 3, Django 6.1, MySQL (utf8mb4) y Bootstrap 5 con el tema de Merkatics.

## Instalar y arrancar

```bash
cd backend
python3 -m venv .venv
MYSQLCLIENT_CFLAGS="-I/usr/local/mysql/include" \
MYSQLCLIENT_LDFLAGS="-L/usr/local/mysql/lib -lmysqlclient -Wl,-rpath,/usr/local/mysql/lib" \
  .venv/bin/pip install -r requirements.txt     # en Mac con el MySQL oficial; en Linux basta pip install
cp .env.example .env                              # y llena los valores
./iniciar_mysql.sh                                # MySQL solo de este proyecto (puerto 3307)
.venv/bin/python manage.py migrate
.venv/bin/python manage.py importar_mvp datos.json
.venv/bin/python manage.py createsuperuser        # pide un WhatsApp de 10 dígitos
.venv/bin/python manage.py runserver              # http://127.0.0.1:8000
```

Sin `DATABASE_NAME` en el `.env` se usa SQLite (para probar rápido).

## Comandos útiles

| Comando | Para qué |
|---|---|
| `manage.py test` | Todas las pruebas automáticas |
| `manage.py probar_conjunto --hora 2026-11-18T12:00-06:00` | Los 108 casos del chat; guarda el resultado en `pruebas/resultados/` |
| `manage.py importar_mvp datos.json` | Carga negocios, preguntas, conversaciones y cuentas; se puede correr varias veces |

## Carpetas

| Carpeta | Qué hay |
|---|---|
| `agente/` | Configuración (`settings.py` lee el `.env`) y `urls.py`, que junta las direcciones de cada app |
| `core/` | Lo común: plantilla base (`templates/layouts/base.html`), partes reutilizables (`templates/partials/`), tema de Bootstrap (`static/core/css/tema.css`), Bootstrap 5 y los iconos Lucide guardados en el proyecto, la etiqueta `{% icono %}`, filtros, widgets y la conexión con Gemini (`ia.py`) |
| `users/` | Cuentas: el dueño entra con su WhatsApp y contraseña |
| `inicio/` | Página de inicio y demo para presentar |
| `negocios/` | Negocio, sus miembros (dueño/encargado) y sus preguntas frecuentes; alta del negocio; `permisos.py` decide quién ve qué |
| `chat/` | Conversaciones, mensajes y avisos; el motor que decide qué contestar (`servicios.py`), el chat del cliente y los avisos al WhatsApp del dueño |
| `panel/` | Panel del dueño y sus reportes |
| `pagos/` | Prueba gratis de 7 días y plan mensual con Stripe |
| `canales/` | WhatsApp real (Meta): qué número es de qué negocio y la dirección que Meta llama |
| `crm/` | Envíos al CRM de Merkatics y su descarga en CSV |
| `media/` | Lo que suben los usuarios (no va en git) |

Cada app tiene `models.py`, `views.py`, `urls.py` (con `app_name`), `forms.py`, `admin.py`, `servicios.py` cuando hay lógica que no es de una pantalla, `templates/<app>/` y `static/<app>/`.

## La base de datos en palabras sencillas

- **usuarios:** las personas que entran al panel (WhatsApp y contraseña).
- **negocios:** cada negocio con su horario, su plan y su enlace de chat.
- **miembros:** qué cuenta es dueña o encargada de qué negocio.
- **preguntas:** las preguntas frecuentes de cada negocio y su respuesta.
- **conversaciones / mensajes:** cada plática con un cliente y lo que se dijo.
- **avisos:** cuando un cliente necesita a una persona (uno pendiente por conversación).
- **canales_whatsapp, whatsapp_recibidos:** el número de WhatsApp de cada negocio y los mensajes ya contestados.
- **envios_crm:** lo que se manda al CRM de Merkatics.

Plan y tickets: `docs/07_Fase_2/01_Plan_y_Backlog.md`.
