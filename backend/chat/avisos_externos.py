"""F2-10 · Avisos fuera del panel: cuando un cliente necesita a una persona,
al dueño le llega un correo (y, con WhatsApp conectado, un WhatsApp).

Sin configuración (sin correo saliente ni WhatsApp) no hace nada: el aviso
sigue llegando al panel como en la Fase 1. Nunca se avisa dos veces por el
mismo aviso.
"""
import logging

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

log = logging.getLogger(__name__)

MOTIVOS = {'no_la_sabe': 'preguntó algo que tu chat no sabe', 'pidio_persona': 'pidió hablar con una persona',
           'pide_cita': 'quiere una cita', 'queja_o_urgencia': 'tiene una queja o urgencia'}


def avisar_si_hace_falta(conversacion):
    from .models import Aviso
    aviso = (Aviso.objects.filter(conversacion=conversacion, estado='pendiente', notificado_en__isnull=True)
             .select_related('negocio').first())
    if aviso is None:
        return False
    negocio = aviso.negocio
    quien = conversacion.cliente_nombre or 'Un cliente'
    asunto = f'{negocio.nombre}: {quien} te necesita'
    cuerpo = (f'{quien} {MOTIVOS[aviso.motivo]}.\n\n«{aviso.mensaje_cliente}»\n\n'
              f'Contéstale desde tu panel: {settings.SITIO_URL}/panel')
    enviado = False

    correos = list(negocio.miembros.select_related('usuario').values_list('usuario__email', flat=True))
    if settings.EMAIL_HOST and correos:
        try:
            send_mail(asunto, cuerpo, settings.DEFAULT_FROM_EMAIL, correos, fail_silently=False)
            enviado = True
        except Exception as e:  # noqa: BLE001 — un correo que falla no rompe el chat
            log.warning('No se pudo mandar el correo de aviso: %s', e)

    if settings.WHATSAPP_TOKEN and settings.WHATSAPP_AVISOS_A_DUENO:
        from canales.whatsapp import avisar_al_dueno
        enviado = avisar_al_dueno(negocio, cuerpo) or enviado

    if enviado:
        aviso.notificado_en = timezone.now()
        aviso.save(update_fields=['notificado_en'])
    return enviado
