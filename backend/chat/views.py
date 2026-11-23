"""Chat del cliente: la pantalla y las direcciones que usa su JavaScript.

El cliente no tiene cuenta: solo conoce el token de su conversación y con él
lee y escribe, nada más.
"""
import json
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from core.ia import redactar
from negocios.models import Negocio

from . import servicios
from .avisos import avisar_si_hace_falta
from .models import Conversacion


def _hora(valor):
    """«23:42» o fecha ISO → fecha con zona (solo cuenta en los negocios de la demo)."""
    if not valor:
        return None
    try:
        if len(valor) <= 5:
            h, m = map(int, valor.split(':'))
            return timezone.localtime().replace(hour=h, minute=m, second=0, microsecond=0)
        return datetime.fromisoformat(valor)
    except ValueError:
        return None


def _mensaje(m, d=None):
    datos = {'id': m.id, 'autor': m.autor, 'texto': m.texto, 'creado_en': m.creado_en.isoformat()}
    if m.opciones:
        datos['opciones'] = m.opciones
    if d:
        datos.update({k: d[k] for k in ('tipo', 'motivo', 'abierto') if d.get(k) is not None})
    return datos


@require_GET
def pantalla(request, slug):
    """La pantalla del chat con aspecto de WhatsApp."""
    negocio = get_object_or_404(Negocio, slug=slug)
    return render(request, 'chat/chat.html', {'negocio': negocio,
                                              'estado': servicios.estado_publico(negocio, _hora(request.GET.get('hora')))})


@require_GET
def estado(request, slug):
    """Nombre, abierto o cerrado, bienvenida y sugerencias."""
    negocio = get_object_or_404(Negocio, slug=slug)
    return JsonResponse(servicios.estado_publico(negocio, _hora(request.GET.get('hora'))))


@require_POST
def iniciar(request, slug):
    """Empieza una conversación nueva y regresa su token."""
    negocio = get_object_or_404(Negocio, slug=slug)
    return JsonResponse({'token': str(Conversacion.objects.create(negocio=negocio).token)}, status=201)


@require_POST
def enviar(request):
    """El cliente manda un mensaje; regresa su mensaje y la respuesta del chat."""
    try:
        datos = json.loads(request.body)
    except ValueError:
        return JsonResponse({'error': 'datos'}, status=400)
    conv = get_object_or_404(Conversacion, token=datos.get('token'), canal='web')
    try:
        cliente, respuesta, d = servicios.recibir(conv, datos.get('texto'), _hora(datos.get('hora')), redactar=redactar)
    except ValueError:
        return JsonResponse({'error': 'texto_invalido'}, status=400)
    avisar_si_hace_falta(conv)
    if d['motivo'] == 'pide_cita':
        from crm.servicios import registrar
        registrar(conv, 'cita')
    return JsonResponse([_mensaje(cliente), _mensaje(respuesta, d)], safe=False)


@require_GET
def mensajes(request):
    """Mensajes nuevos de la conversación (el chat pregunta cada pocos segundos)."""
    conv = get_object_or_404(Conversacion, token=request.GET.get('token'))
    despues = int(request.GET.get('despues_de') or 0)
    return JsonResponse([_mensaje(m) for m in conv.mensajes.filter(id__gt=despues).order_by('id')], safe=False)
