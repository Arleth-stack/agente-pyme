"""Avisos fuera del panel: cuando un cliente necesita a una persona, al dueño le
llega un WhatsApp a su número. Sin WhatsApp conectado, el aviso sigue solo en el panel."""
import logging

from django.conf import settings
from django.utils import timezone

log = logging.getLogger(__name__)

MOTIVOS = {'no_la_sabe': 'preguntó algo que tu chat no sabe', 'pidio_persona': 'pidió hablar con una persona',
           'pide_cita': 'quiere una cita', 'queja_o_urgencia': 'tiene una queja o urgencia'}


def texto_del_aviso(aviso, conversacion):
    """El mensaje que recibe el dueño."""
    quien = conversacion.cliente_nombre or 'Un cliente'
    return (f'{aviso.negocio.nombre}: {quien} {MOTIVOS[aviso.motivo]}.\n\n«{aviso.mensaje_cliente}»\n\n'
            f'Contéstale desde tu panel: {settings.SITIO_URL}/panel/')


def avisar_si_hace_falta(conversacion):
    """Manda el aviso pendiente al WhatsApp del dueño una sola vez."""
    from canales.servicios import avisar_al_dueno

    from .models import Aviso
    aviso = (Aviso.objects.filter(conversacion=conversacion, estado='pendiente', notificado_en__isnull=True)
             .select_related('negocio').first())
    if aviso is None or not (settings.WHATSAPP_TOKEN and settings.WHATSAPP_AVISOS_A_DUENO):
        return False
    if not avisar_al_dueno(aviso.negocio, texto_del_aviso(aviso, conversacion)):
        return False
    aviso.notificado_en = timezone.now()
    aviso.save(update_fields=['notificado_en'])
    return True
