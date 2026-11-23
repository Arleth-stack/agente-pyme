"""Dirección que Meta llama con cada mensaje de WhatsApp."""
import hmac
import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from .servicios import firma_valida, procesar


@csrf_exempt
def webhook(request):
    """Verificación inicial (GET) y mensajes entrantes (POST, con firma de la app)."""
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
