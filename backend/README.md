# Backend de la Fase 2 (Python · Django · MySQL)

## Arrancar en la compu

```bash
cd backend
./iniciar_mysql.sh                      # MySQL solo de este proyecto (puerto 3307)
.venv/bin/python manage.py migrate      # crea o actualiza las tablas
.venv/bin/python manage.py runserver    # http://127.0.0.1:8000
```

La primera vez (en otra compu): `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`, copiar `.env.example` como `.env` y llenarlo.

## Comandos útiles

| Comando | Para qué |
|---|---|
| `.venv/bin/python manage.py test` | Todas las pruebas automáticas (aislamiento, chat, redacción, WhatsApp, CRM) |
| `.venv/bin/python manage.py probar_conjunto --hora 2026-11-18T12:00-06:00` | Los 108 casos del chat (P1); guarda el resultado en `pruebas/resultados/` |
| `.venv/bin/python manage.py importar_fase1 archivo.json` | Mudanza de los datos de Supabase (F2-05) |
| `.venv/bin/python manage.py createsuperuser` | Cuenta para entrar a `/admin` |

## Cómo está armado

| Carpeta | Qué hay |
|---|---|
| `agente/` | Configuración (`settings.py` lee todo lo secreto de `.env`) y direcciones (`urls.py`) |
| `negocios/` | Negocio, Miembro (dueño/encargado), Pregunta; cuentas, alta y panel (`api.py`); aislamiento (`servicios.negocio_de`) |
| `chat/` | Conversación, Mensaje, Aviso; el motor (`motor.py`), el chat público (`api.py`), la redacción con Gemini (`redaccion.py`) y los avisos fuera del panel (`avisos_externos.py`) |
| `canales/` | WhatsApp real con Meta (`whatsapp.py`) y qué número es de qué negocio |
| `crm/` | Envíos al CRM de Merkatics y su descarga en CSV |

Plan y tickets: `docs/07_Fase_2/01_Plan_y_Backlog.md`.
