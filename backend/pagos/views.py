"""Botones del plan (registrar tarjeta, administrar) y avisos que manda Stripe."""
import json
import re

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from negocios.models import Negocio
from negocios.permisos import con_negocio

from . import servicios


def _origen(request):
    return request.build_absolute_uri('/').rstrip('/') or settings.SITIO_URL


@require_POST
@con_negocio(solo_dueno=True)
def prueba(request):
    """Lleva al dueño a la página de Stripe para registrar su tarjeta."""
    n = request.negocio
    if n.es_demo or n.plan_estado in ('prueba', 'activa'):
        return redirect('panel:inicio')
    try:
        return redirect(servicios.url_pago(n, request.user, _origen(request)))
    except servicios.ErrorStripe:
        messages.error(request, 'No pudimos abrir la página de pago. Revisa tu internet e inténtalo de nuevo.')
        return redirect('panel:inicio')


@require_POST
@con_negocio(solo_dueno=True)
def portal(request):
    """Lleva al dueño a la página de Stripe de su plan."""
    n = request.negocio
    if n.es_demo or not n.stripe_cliente:
        return redirect('panel:inicio')
    try:
        return redirect(servicios.url_portal(n, _origen(request)))
    except servicios.ErrorStripe:
        messages.error(request, 'No pudimos abrir la página de tu plan. Inténtalo de nuevo.')
        return redirect('panel:inicio')


@csrf_exempt
@require_POST
def aviso_stripe(request):
    """Stripe avisa cada cambio de una suscripción; se acepta solo con firma válida."""
    if not servicios.firma_valida(request.body, request.headers.get('Stripe-Signature')):
        return HttpResponse('firma', status=400)
    evento = json.loads(request.body)
    if not str(evento.get('type', '')).startswith('customer.subscription.'):
        return HttpResponse('ok')
    s = evento['data']['object']
    negocio_id = (s.get('metadata') or {}).get('negocio_id', '')
    if not re.fullmatch(r'[0-9a-f-]{36}', negocio_id) or not Negocio.objects.filter(id=negocio_id).exists():
        return HttpResponse('sin negocio')
    servicios.guardar_plan(negocio_id, s)
    return HttpResponse('ok')
