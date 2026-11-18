"""F2-09 · WhatsApp real con la Cloud API de Meta.

Recorrido: el cliente escribe al WhatsApp del negocio → Meta llama a
/api/whatsapp/webhook → el mismo motor del chat decide → se contesta por
WhatsApp. Si el dueño contesta desde el panel, también sale por WhatsApp.

Reglas de Meta que hay que respetar:
- Solo se puede escribir texto libre dentro de las 24 h siguientes al último
  mensaje del cliente («ventana de atención»). Fuera de ella se necesita una
  plantilla aprobada por Meta; en ese caso no se envía y el panel lo indica.
- Cada llamada al webhook se comprueba con la firma de la app (APP_SECRET).
"""
import hashlib
import hmac
import json
import logging
from datetime import timedelta

import requests
from django.conf import settings
from django.db import IntegrityError, transaction
from django.http import HttpResponse, HttpResponseForbidden
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from chat import motor
from chat.avisos_externos import avisar_si_hace_falta
from chat.models import Conversacion
from chat.redaccion import redactar

from .models import CanalWhatsApp, RecibidoWhatsApp

log = logging.getLogger(__name__)
VENTANA = timedelta(hours=24)


def _graph(phone_number_id):
    version = getattr(settings, 'WHATSAPP_API_VERSION', None) or 'v23.0'
    return f'https://graph.facebook.com/{version}/{phone_number_id}/messages'


def _mandar(phone_number_id, para, texto):
    if not settings.WHATSAPP_TOKEN:
        return False
    try:
        r = requests.post(_graph(phone_number_id), timeout=10,
                          headers={'Authorization': f'Bearer {settings.WHATSAPP_TOKEN}'},
                          json={'messaging_product': 'whatsapp', 'recipient_type': 'individual', 'to': para,
                                'type': 'text', 'text': {'preview_url': False, 'body': texto[:4096]}})
    except requests.RequestException as e:
        log.warning('WhatsApp no respondió: %s', e)
        return False
    if r.status_code >= 300:
        log.warning('WhatsApp rechazó el envío (%s): %s', r.status_code, r.text[:300])
        return False
    return True


def enviar_texto(conversacion, texto):
    """Respuesta del dueño desde el panel hacia el WhatsApp del cliente."""
    canal = CanalWhatsApp.objects.filter(negocio_id=conversacion.negocio_id, activo=True).first()
    if canal is None or not conversacion.whatsapp_cliente:
        return False
    ultimo = conversacion.ultimo_mensaje_cliente_en
    if ultimo is None or timezone.now() - ultimo > VENTANA:
        return False  # fuera de las 24 h: Meta pide plantilla
    return _mandar(canal.phone_number_id, conversacion.whatsapp_cliente, texto)


def avisar_al_dueno(negocio, texto):
    canal = CanalWhatsApp.objects.filter(negocio=negocio, activo=True).exclude(dueno_whatsapp='').first()
    return bool(canal) and _mandar(canal.phone_number_id, canal.dueno_whatsapp, texto)


def firma_valida(cuerpo, encabezado):
    secreto = settings.WHATSAPP_APP_SECRET
    if not secreto or not encabezado or not encabezado.startswith('sha256='):
        return False
    esperada = hmac.new(secreto.encode(), cuerpo, hashlib.sha256).hexdigest()
    return hmac.compare_digest(esperada, encabezado.split('=', 1)[1])


def _conversacion(negocio, numero, nombre):
    """Una conversación por cliente; si pasó más de una semana sin hablar, empieza otra."""
    conv = (Conversacion.objects.filter(negocio=negocio, canal='whatsapp', whatsapp_cliente=numero)
            .order_by('-ultimo_mensaje_en').first())
    if conv is None or timezone.now() - conv.ultimo_mensaje_en > timedelta(days=7):
        conv = Conversacion.objects.create(negocio=negocio, canal='whatsapp', whatsapp_cliente=numero,
                                           cliente_nombre=(nombre or '')[:60] or None,
                                           cliente_telefono=numero[-10:] if len(numero) >= 10 else None)
    return conv


def procesar(valor):
    """Un bloque «value» del webhook: mensajes entrantes de un número del negocio."""
    phone_id = (valor.get('metadata') or {}).get('phone_number_id')
    canal = CanalWhatsApp.objects.select_related('negocio').filter(phone_number_id=phone_id, activo=True).first()
    if canal is None:
        return 0
    nombres = {c.get('wa_id'): (c.get('profile') or {}).get('name') for c in valor.get('contacts', [])}
    contestados = 0
    for m in valor.get('messages', []):
        try:
            with transaction.atomic():
                RecibidoWhatsApp.objects.create(wamid=m['id'])
        except IntegrityError:
            continue  # ya se contestó
        numero = m.get('from')
        conv = _conversacion(canal.negocio, numero, nombres.get(numero))
        if m.get('type') == 'text':
            texto = (m.get('text') or {}).get('body', '')
        elif m.get('type') == 'interactive':
            i = m.get('interactive') or {}
            texto = (i.get('button_reply') or i.get('list_reply') or {}).get('title', '')
        else:
            # Audios, fotos, ubicaciones: por ahora se le pasa al equipo.
            texto = '(El cliente mandó un archivo o audio)'
        try:
            _, respuesta, d = motor.recibir(conv, texto[:1000] or '…', redactar=redactar)
        except ValueError:
            continue
        _mandar(canal.phone_number_id, numero, respuesta.texto)
        avisar_si_hace_falta(conv)
        if d['motivo'] == 'pide_cita':
            from crm.servicios import registrar
            registrar(conv, 'cita')
        contestados += 1
    return contestados


@csrf_exempt
def webhook(request):
    if request.method == 'GET':
        # Verificación inicial que hace Meta al registrar la dirección.
        if (request.GET.get('hub.mode') == 'subscribe' and settings.WHATSAPP_VERIFY_TOKEN
                and hmac.compare_digest(request.GET.get('hub.verify_token', ''), settings.WHATSAPP_VERIFY_TOKEN)):
            return HttpResponse(request.GET.get('hub.challenge', ''), content_type='text/plain')
        return HttpResponseForbidden('token')
    if request.method != 'POST':
        return HttpResponse(status=405)
    if not firma_valida(request.body, request.headers.get('X-Hub-Signature-256')):
        return HttpResponseForbidden('firma')
    try:
        datos = json.loads(request.body)
    except ValueError:
        return HttpResponse(status=400)
    for entrada in datos.get('entry', []):
        for cambio in entrada.get('changes', []):
            if cambio.get('field') == 'messages':
                procesar(cambio.get('value') or {})
    return HttpResponse('ok')
