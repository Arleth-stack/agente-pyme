"""WhatsApp real con la Cloud API de Meta.

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
import logging
from datetime import timedelta

import requests
from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone

from chat import servicios as motor
from chat.avisos import avisar_si_hace_falta
from chat.models import Conversacion
from core.ia import redactar

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


def numero_del_dueno(negocio):
    """WhatsApp del dueño con lada de México (52 + sus 10 dígitos), o el que se puso en el canal."""
    canal = CanalWhatsApp.objects.filter(negocio=negocio).first()
    if canal and canal.dueno_whatsapp:
        return canal.dueno_whatsapp
    dueno = negocio.miembros.filter(rol='dueno').select_related('usuario').first()
    return f'52{dueno.usuario.telefono}' if dueno else None


def avisar_al_dueno(negocio, texto):
    """Manda el aviso al WhatsApp del dueño desde el número del negocio."""
    canal = CanalWhatsApp.objects.filter(negocio=negocio, activo=True).first()
    numero = numero_del_dueno(negocio)
    return bool(canal and numero) and _mandar(canal.phone_number_id, numero, texto)


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
