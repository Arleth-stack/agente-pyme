"""F2-11 · Qué se manda al CRM y cuándo (docs/05_Integracion_Merkatics, secciones 2 y 3).

- Cuándo: al pedir una cita (prospecto caliente) y al marcar una conversación como resuelta.
- Qué: solo el resumen (no los mensajes completos): nombre, teléfono, organización,
  interés, resumen, atención, fechas y origen.
- Cómo: si hay dirección del CRM (MERKATICS_CRM_URL) se envía directo; si no,
  queda en la tabla y se descarga en CSV para importarlo en Merkatics.
"""
import logging

import requests
from django.conf import settings
from django.utils import timezone

from .models import EnvioCRM

log = logging.getLogger(__name__)
MOTIVOS = {'no_la_sabe': 'no la sabe', 'pidio_persona': 'pidió una persona', 'pide_cita': 'pide una cita',
           'queja_o_urgencia': 'queja o urgencia'}


def datos_de(conv):
    mensajes = list(conv.mensajes.order_by('id').values('autor', 'texto', 'creado_en'))
    avisos = list(conv.avisos.order_by('-creado_en').values('motivo'))
    del_cliente = [m['texto'] for m in mensajes if m['autor'] == 'cliente']
    resumen = conv.resumen or (' · '.join(del_cliente[-2:]))[:200]
    atencion = (f"necesitó persona · {MOTIVOS[avisos[0]['motivo']]}" if avisos else 'la resolvió el asistente')
    fecha = lambda d: timezone.localtime(d).strftime('%d/%m/%Y %H:%M') if d else ''  # noqa: E731
    return {
        'nombre': conv.cliente_nombre or '',
        'telefono': conv.cliente_telefono or conv.whatsapp_cliente or '',
        'organizacion': conv.negocio.merkatics_org_id or '',
        'negocio': conv.negocio.nombre,
        'interes': conv.interes or 'otro',
        'resumen': resumen,
        'atencion': atencion,
        'primer_mensaje': fecha(mensajes[0]['creado_en']) if mensajes else '',
        'ultimo_mensaje': fecha(mensajes[-1]['creado_en']) if mensajes else '',
        'origen': 'Agente de WhatsApp',
    }


def registrar(conv, motivo):
    """Guarda el envío (uno por conversación y motivo mientras siga pendiente) y lo manda si hay CRM."""
    conv.refresh_from_db()  # el motor acaba de cambiar el interés y el estado
    if conv.negocio.es_demo:
        return None
    envio = EnvioCRM.objects.filter(conversacion=conv, motivo=motivo, estado='pendiente').first()
    datos = datos_de(conv)
    if envio:
        envio.datos = datos
        envio.save(update_fields=['datos'])
    else:
        envio = EnvioCRM.objects.create(negocio=conv.negocio, conversacion=conv, motivo=motivo, datos=datos)
    url = getattr(settings, 'MERKATICS_CRM_URL', '')
    if url:
        try:
            r = requests.post(url, json={'motivo': motivo, **datos}, timeout=8,
                              headers={'Authorization': f"Bearer {getattr(settings, 'MERKATICS_CRM_TOKEN', '')}"})
            envio.estado = 'enviado' if r.status_code < 300 else 'fallo'
            envio.respuesta = f'{r.status_code} {r.text[:250]}'
        except requests.RequestException as e:
            envio.estado, envio.respuesta = 'fallo', str(e)[:300]
        envio.enviado_en = timezone.now()
        envio.save(update_fields=['estado', 'respuesta', 'enviado_en'])
    return envio
