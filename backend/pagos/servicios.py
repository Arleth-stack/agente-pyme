"""Prueba gratis de 7 días y plan mensual con Stripe (modo de prueba)."""
import hashlib
import hmac
import re
import time
from datetime import datetime, timedelta
from datetime import timezone as tz

import requests
from django.conf import settings
from django.utils import timezone

from negocios.models import Negocio

DIAS_PRUEBA = 7
TOLERANCIA_S = 300
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre',
         'noviembre', 'diciembre']


class ErrorStripe(Exception):
    """Stripe rechazó la petición o no contestó."""


def _form(obj, prefijo='', partes=None):
    """Convierte un diccionario anidado al formato de formulario que pide Stripe."""
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
    """Llamada a la API de Stripe."""
    try:
        r = requests.request(metodo, f'https://api.stripe.com/v1/{ruta}', timeout=15,
                             headers={'Authorization': f'Bearer {settings.STRIPE_SECRET_KEY}'},
                             data=_form(datos) if datos else None)
    except requests.RequestException as e:
        raise ErrorStripe(str(e)) from e
    cuerpo = r.json()
    if r.status_code >= 300:
        raise ErrorStripe(cuerpo.get('error', {}).get('message', r.status_code))
    return cuerpo


def estado_de(suscripcion):
    """Estado de Stripe → estado del plan."""
    return {'trialing': 'prueba', 'active': 'activa', 'past_due': 'pago_pendiente', 'unpaid': 'pago_pendiente',
            'incomplete': 'pago_pendiente'}.get(suscripcion.get('status'), 'cancelada')


def _fecha(segundos):
    return datetime.fromtimestamp(segundos, tz=tz.utc) if segundos else None


def guardar_plan(negocio_id, s):
    """Guarda lo que dice Stripe sin que un aviso viejo pise a la suscripción vigente."""
    estado = estado_de(s)
    qs = Negocio.objects.filter(id=negocio_id)
    if estado not in ('prueba', 'activa'):
        qs = qs.filter(stripe_suscripcion__isnull=True) | qs.filter(stripe_suscripcion=s['id'])
    cliente = s.get('customer')
    qs.update(plan_estado=estado, prueba_termina=_fecha(s.get('trial_end')), plan_termina=_fecha(s.get('cancel_at')),
              stripe_cliente=cliente if isinstance(cliente, str) else (cliente or {}).get('id'),
              stripe_suscripcion=s['id'], plan_actualizado=timezone.now())
    return Negocio.objects.get(id=negocio_id)


def sincronizar(negocio, sesion_pago=None):
    """Confirma con Stripe el estado del plan (al volver del pago o al abrir el panel)."""
    if negocio.es_demo or not settings.STRIPE_SECRET_KEY:
        return negocio
    try:
        sub = None
        if sesion_pago and re.fullmatch(r'cs_[A-Za-z0-9_]+', sesion_pago):
            pago = stripe(f'checkout/sessions/{sesion_pago}?expand[]=subscription')
            if pago.get('client_reference_id') == str(negocio.id) and isinstance(pago.get('subscription'), dict):
                sub = pago['subscription']
        elif negocio.stripe_suscripcion:
            sub = stripe(f'subscriptions/{negocio.stripe_suscripcion}')
        return guardar_plan(negocio.id, sub) if sub else negocio
    except ErrorStripe:
        return negocio  # se muestra lo último guardado


def fecha_larga(fecha):
    """13 de noviembre."""
    return f'{fecha.day} de {MESES[fecha.month - 1]}'


def url_pago(negocio, usuario, origen):
    """Abre la página segura de Stripe para registrar la tarjeta (7 días gratis la primera vez)."""
    primera_vez = not negocio.stripe_suscripcion
    cobro = fecha_larga(timezone.localdate() + timedelta(days=DIAS_PRUEBA))
    mensaje = (f'Hoy no se te cobra nada. El {cobro} se cobra 1 dólar por tu primer mes y después cada mes. '
               'Puedes cancelar cuando quieras desde tu panel.' if primera_vez else
               'Se cobra 1 dólar hoy y después cada mes. Puedes cancelar cuando quieras desde tu panel.')
    pago = stripe('checkout/sessions', metodo='POST', datos={
        'mode': 'subscription', 'locale': 'es-419', 'client_reference_id': str(negocio.id),
        **({'customer': negocio.stripe_cliente} if negocio.stripe_cliente
           else ({'customer_email': usuario.correo} if usuario.correo else {})),
        'line_items': {'0': {'price': settings.STRIPE_PRICE_ID, 'quantity': 1}},
        'payment_method_collection': 'always',
        'metadata': {'negocio_id': str(negocio.id)},
        'subscription_data': {'metadata': {'negocio_id': str(negocio.id), 'negocio': negocio.slug},
                              **({'trial_period_days': DIAS_PRUEBA} if primera_vez else {})},
        'custom_text': {'submit': {'message': mensaje}},
        'success_url': f'{origen}/panel/?plan=listo&s={{CHECKOUT_SESSION_ID}}',
        'cancel_url': f'{origen}/panel/?plan=cancelado',
    })
    return pago['url']


def url_portal(negocio, origen):
    """Página de Stripe para cambiar tarjeta, ver cobros o cancelar."""
    p = stripe('billing_portal/sessions', metodo='POST', datos={
        'customer': negocio.stripe_cliente, 'locale': 'es-419', 'return_url': f'{origen}/panel/?plan=volvio',
        **({'configuration': settings.STRIPE_PORTAL_ID} if settings.STRIPE_PORTAL_ID else {})})
    return p['url']


def firma_valida(cuerpo, encabezado):
    """Comprueba que el aviso viene de Stripe."""
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
