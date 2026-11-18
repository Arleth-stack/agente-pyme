"""F2-07 · Prueba gratis de 7 días y plan mensual con Stripe (modo de prueba).

Traducción de las funciones de Vercel de la Fase 1 (api/prueba.js, plan.js,
portal.js y stripe-aviso.js). La tarjeta solo se escribe en la página de
Stripe; aquí solo se guarda en qué va cada negocio.
"""
import hashlib
import hmac
import json
import re
import time
from datetime import datetime, timedelta
from datetime import timezone as tz

import requests
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Negocio
from .servicios import negocio_de

DIAS_PRUEBA = 7
TOLERANCIA_S = 300


class ErrorStripe(Exception):
    pass


def _form(obj, prefijo='', partes=None):
    partes = [] if partes is None else partes
    for k, v in obj.items():
        if v is None:
            continue
        llave = f'{prefijo}[{k}]' if prefijo else k
        if isinstance(v, dict):
            _form(v, llave, partes)
        else:
            partes.append((llave, str(v).lower() if isinstance(v, bool) else str(v)))
    return partes


def stripe(ruta, datos=None, metodo='GET'):
    r = requests.request(metodo, f'https://api.stripe.com/v1/{ruta}', timeout=15,
                         headers={'Authorization': f'Bearer {settings.STRIPE_SECRET_KEY}'},
                         data=_form(datos) if datos else None)
    cuerpo = r.json()
    if r.status_code >= 300:
        raise ErrorStripe(cuerpo.get('error', {}).get('message', r.status_code))
    return cuerpo


def estado_de(suscripcion):
    return {'trialing': 'prueba', 'active': 'activa', 'past_due': 'pago_pendiente', 'unpaid': 'pago_pendiente',
            'incomplete': 'pago_pendiente'}.get(suscripcion.get('status'), 'cancelada')


def _fecha(segundos):
    return datetime.fromtimestamp(segundos, tz=tz.utc) if segundos else None


def guardar_plan(negocio_id, s):
    """Guarda lo que dice Stripe. Un aviso viejo (p. ej. la cancelación de una
    suscripción anterior) no pisa a la suscripción vigente."""
    estado = estado_de(s)
    qs = Negocio.objects.filter(id=negocio_id)
    if estado not in ('prueba', 'activa'):
        qs = qs.filter(stripe_suscripcion__isnull=True) | qs.filter(stripe_suscripcion=s['id'])
    cliente = s.get('customer')
    qs.update(plan_estado=estado, prueba_termina=_fecha(s.get('trial_end')), plan_termina=_fecha(s.get('cancel_at')),
              stripe_cliente=cliente if isinstance(cliente, str) else (cliente or {}).get('id'),
              stripe_suscripcion=s['id'], plan_actualizado=timezone.now())
    return Negocio.objects.get(id=negocio_id)


def resumen(n):
    return {'es_demo': n.es_demo, 'estado': n.plan_estado, 'prueba_termina': n.prueba_termina,
            'plan_termina': n.plan_termina, 'puede_probar': not n.stripe_suscripcion,
            'puede_administrar': bool(n.stripe_cliente)}


def _origen(request):
    return request.headers.get('Origin') or settings.SITIO_URL


@api_view(['POST'])
def prueba(request):
    n = negocio_de(request.user, solo_dueno=True)
    if n.es_demo:
        return Response({'error': 'demo'}, status=400)
    if n.plan_estado in ('prueba', 'activa'):
        return Response({'url': '/panel'})
    primera_vez = not n.stripe_suscripcion
    cobro = (timezone.localdate() + timedelta(days=DIAS_PRUEBA)).strftime('%-d de %B') if primera_vez else ''
    origen = _origen(request)
    try:
        pago = stripe('checkout/sessions', metodo='POST', datos={
            'mode': 'subscription', 'locale': 'es-419', 'client_reference_id': str(n.id),
            **({'customer': n.stripe_cliente} if n.stripe_cliente else {'customer_email': request.user.email}),
            'line_items': {'0': {'price': settings.STRIPE_PRICE_ID, 'quantity': 1}},
            'payment_method_collection': 'always',
            'metadata': {'negocio_id': str(n.id)},
            'subscription_data': {'metadata': {'negocio_id': str(n.id), 'negocio': n.slug},
                                  **({'trial_period_days': DIAS_PRUEBA} if primera_vez else {})},
            'custom_text': {'submit': {'message': (
                f'Hoy no se te cobra nada. El {cobro} se cobra 1 dólar por tu primer mes y después cada mes. '
                'Puedes cancelar cuando quieras desde tu panel.') if primera_vez else (
                'Se cobra 1 dólar hoy y después cada mes. Puedes cancelar cuando quieras desde tu panel.')}},
            'success_url': f'{origen}/panel?plan=listo&s={{CHECKOUT_SESSION_ID}}',
            'cancel_url': f'{origen}/panel?plan=cancelado',
        })
    except (ErrorStripe, requests.RequestException):
        return Response({'error': 'stripe'}, status=502)
    return Response({'url': pago['url']})


@api_view(['POST'])
def plan(request):
    n = negocio_de(request.user)
    if n.es_demo:
        return Response(resumen(n))
    s = request.data.get('s')
    try:
        sub = None
        if isinstance(s, str) and re.fullmatch(r'cs_[A-Za-z0-9_]+', s):
            pago = stripe(f'checkout/sessions/{s}?expand[]=subscription')
            if pago.get('client_reference_id') == str(n.id) and isinstance(pago.get('subscription'), dict):
                sub = pago['subscription']
        elif n.stripe_suscripcion:
            sub = stripe(f'subscriptions/{n.stripe_suscripcion}')
        if sub:
            n = guardar_plan(n.id, sub)
    except (ErrorStripe, requests.RequestException):
        pass  # se muestra lo último guardado
    return Response(resumen(n))


@api_view(['POST'])
def portal(request):
    n = negocio_de(request.user, solo_dueno=True)
    if n.es_demo or not n.stripe_cliente:
        return Response({'error': 'sin_tarjeta'}, status=400)
    try:
        p = stripe('billing_portal/sessions', metodo='POST', datos={
            'customer': n.stripe_cliente, 'locale': 'es-419', 'return_url': f'{_origen(request)}/panel?plan=volvio',
            **({'configuration': settings.STRIPE_PORTAL_ID} if settings.STRIPE_PORTAL_ID else {})})
    except (ErrorStripe, requests.RequestException):
        return Response({'error': 'stripe'}, status=502)
    return Response({'url': p['url']})


def firma_valida(cuerpo, encabezado):
    secreto = settings.STRIPE_WEBHOOK_SECRET
    if not secreto or not encabezado:
        return False
    partes = [p.split('=', 1) for p in encabezado.split(',') if '=' in p]
    t = next((v for k, v in partes if k == 't'), None)
    firmas = [v for k, v in partes if k == 'v1']
    if not t or not firmas or abs(time.time() - int(t)) > TOLERANCIA_S:
        return False
    esperada = hmac.new(secreto.encode(), f'{t}.'.encode() + cuerpo, hashlib.sha256).hexdigest()
    return any(hmac.compare_digest(esperada, f) for f in firmas)


@csrf_exempt
def aviso_stripe(request):
    if request.method != 'POST':
        return HttpResponse(status=405)
    if not firma_valida(request.body, request.headers.get('Stripe-Signature')):
        return HttpResponse('firma', status=400)
    evento = json.loads(request.body)
    if not str(evento.get('type', '')).startswith('customer.subscription.'):
        return HttpResponse('ok')
    s = evento['data']['object']
    negocio_id = (s.get('metadata') or {}).get('negocio_id', '')
    if not re.fullmatch(r'[0-9a-f-]{36}', negocio_id) or not Negocio.objects.filter(id=negocio_id).exists():
        return HttpResponse('sin negocio')
    guardar_plan(negocio_id, s)
    return HttpResponse('ok')
