"""Pruebas del canal de WhatsApp (F2-09) y del envío al CRM (F2-11), sin llamar a Meta de verdad."""
import hashlib
import hmac
import json
from datetime import timedelta
from unittest import mock

from django.test import TestCase, override_settings
from django.utils import timezone

from chat.models import Conversacion
from chat.tests import salon
from crm.models import EnvioCRM

from .models import CanalWhatsApp

SECRETO = 'secreto-de-prueba'


def mensaje(texto, wamid='wamid.1', numero='5215511112222'):
    return {'object': 'whatsapp_business_account', 'entry': [{'changes': [{'field': 'messages', 'value': {
        'metadata': {'phone_number_id': '111'},
        'contacts': [{'wa_id': numero, 'profile': {'name': 'Mariana'}}],
        'messages': [{'id': wamid, 'from': numero, 'type': 'text', 'text': {'body': texto}}]}}]}]}


@override_settings(WHATSAPP_TOKEN='token', WHATSAPP_VERIFY_TOKEN='verifica', WHATSAPP_APP_SECRET=SECRETO,
                   GEMINI_API_KEY='')
class WhatsAppTest(TestCase):
    def setUp(self):
        self.n = salon()
        CanalWhatsApp.objects.create(negocio=self.n, phone_number_id='111')

    def post(self, cuerpo, firma=True):
        crudo = json.dumps(cuerpo).encode()
        h = {'HTTP_X_HUB_SIGNATURE_256': 'sha256=' + hmac.new(SECRETO.encode(), crudo, hashlib.sha256).hexdigest()}
        return self.client.post('/api/whatsapp/webhook', crudo, content_type='application/json',
                                **(h if firma else {}))

    def test_verificacion_de_meta(self):
        r = self.client.get('/api/whatsapp/webhook', {'hub.mode': 'subscribe', 'hub.verify_token': 'verifica',
                                                      'hub.challenge': '12345'})
        self.assertEqual(r.content, b'12345')
        r = self.client.get('/api/whatsapp/webhook', {'hub.mode': 'subscribe', 'hub.verify_token': 'otro'})
        self.assertEqual(r.status_code, 403)

    def test_sin_firma_no_entra(self):
        self.assertEqual(self.post(mensaje('hola'), firma=False).status_code, 403)

    @mock.patch('canales.whatsapp.requests.post')
    def test_contesta_por_whatsapp_y_una_sola_vez(self, post):
        post.return_value = mock.Mock(status_code=200)
        self.post(mensaje('cuanto cuesta el corte de dama?'))
        self.post(mensaje('cuanto cuesta el corte de dama?'))  # Meta lo reenvía: se ignora
        self.assertEqual(post.call_count, 1)
        cuerpo = post.call_args.kwargs['json']
        self.assertEqual(cuerpo['to'], '5215511112222')
        self.assertEqual(cuerpo['text']['body'], 'El corte de dama cuesta $250.')
        conv = Conversacion.objects.get(canal='whatsapp')
        self.assertEqual((conv.cliente_nombre, conv.cliente_telefono), ('Mariana', '5511112222'))

    @mock.patch('canales.whatsapp.requests.post')
    def test_cita_por_whatsapp_llega_al_crm(self, post):
        post.return_value = mock.Mock(status_code=200)
        self.post(mensaje('quiero una cita el sábado a las 11', wamid='wamid.2'))
        envio = EnvioCRM.objects.get(motivo='cita')
        self.assertEqual(envio.datos['nombre'], 'Mariana')
        self.assertEqual(envio.datos['interes'], 'cita')
        self.assertEqual(envio.datos['origen'], 'Agente de WhatsApp')

    @mock.patch('canales.whatsapp.requests.post')
    def test_respuesta_del_dueno_fuera_de_24_horas_no_se_envia(self, post):
        from canales.whatsapp import enviar_texto
        conv = Conversacion.objects.create(negocio=self.n, canal='whatsapp', whatsapp_cliente='5215511112222',
                                           ultimo_mensaje_cliente_en=timezone.now() - timedelta(hours=30))
        self.assertFalse(enviar_texto(conv, 'Hola'))
        post.assert_not_called()
