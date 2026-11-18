"""API pública del chat (sin cuenta): la usa el cliente del negocio.

Equivale a las funciones chat_* de la Fase 1. El cliente solo conoce el token
de su conversación; con él lee y escribe, y nada más.
"""
from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from negocios.models import Negocio

from . import motor
from .models import Conversacion, Mensaje


class LimiteChat(ScopedRateThrottle):
    scope_attr = 'throttle_scope'

    def get_rate(self):
        return '30/min'


def _hora(valor):
    """«23:42» o ISO completo → fecha con zona; solo la usan los negocios de la demo."""
    if not valor:
        return None
    try:
        if len(valor) <= 5:
            from django.utils import timezone
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


publico = [authentication_classes([]), permission_classes([])]


def sin_cuenta(vista):
    for deco in reversed(publico):
        vista = deco(vista)
    return vista


@api_view(['GET'])
@sin_cuenta
def negocio(request, slug):
    n = get_object_or_404(Negocio, slug=slug)
    return Response(motor.estado_publico(n, _hora(request.GET.get('hora'))))


@api_view(['POST'])
@sin_cuenta
def iniciar(request, slug):
    n = get_object_or_404(Negocio, slug=slug)
    conv = Conversacion.objects.create(negocio=n)
    return Response({'token': str(conv.token)}, status=201)


@api_view(['POST'])
@sin_cuenta
@throttle_classes([LimiteChat])
def enviar(request):
    conv = get_object_or_404(Conversacion, token=request.data.get('token'), canal='web')
    from .redaccion import redactar
    try:
        cliente, respuesta, d = motor.recibir(conv, request.data.get('texto'), _hora(request.data.get('hora')),
                                              redactar=redactar)
    except ValueError:
        return Response({'error': 'texto_invalido'}, status=400)
    from .avisos_externos import avisar_si_hace_falta
    avisar_si_hace_falta(conv)
    if d['motivo'] == 'pide_cita':
        from crm.servicios import registrar
        registrar(conv, 'cita')
    return Response([_mensaje(cliente), _mensaje(respuesta, d)])


@api_view(['GET'])
@sin_cuenta
def mensajes(request):
    conv = get_object_or_404(Conversacion, token=request.GET.get('token'))
    despues = int(request.GET.get('despues_de') or 0)
    return Response([_mensaje(m) for m in conv.mensajes.filter(id__gt=despues).order_by('id')])


@api_view(['GET'])
@sin_cuenta
def negocios_demo(request):
    return Response([{'slug': n.slug, 'nombre': n.nombre} for n in Negocio.objects.filter(es_demo=True)])
