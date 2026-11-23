"""Pruebas de los avisos de Stripe (sin llamar a Stripe de verdad)."""
import hashlib
import hmac
import json
import time

from django.test import TestCase, override_settings

from negocios.tests import negocio_con_dueno


@override_settings(STRIPE_WEBHOOK_SECRET='whsec_prueba')
class AvisoStripeTest(TestCase):
    def setUp(self):
        self.n, _, _ = negocio_con_dueno('Salon D', '5511110005')

    def mandar(self, firma=None):
        evento = {'type': 'customer.subscription.updated', 'data': {'object': {
            'id': 'sub_123', 'status': 'trialing', 'customer': 'cus_1', 'trial_end': int(time.time()) + 7 * 86400,
            'cancel_at': None, 'metadata': {'negocio_id': str(self.n.id)}}}}
        crudo = json.dumps(evento).encode()
        t = str(int(time.time()))
        firma = firma or hmac.new(b'whsec_prueba', f'{t}.'.encode() + crudo, hashlib.sha256).hexdigest()
        return self.client.post('/pagos/aviso-stripe/', crudo, content_type='application/json',
                                HTTP_STRIPE_SIGNATURE=f't={t},v1={firma}')

    def test_sin_firma_valida_no_cambia_nada(self):
        self.assertEqual(self.mandar(firma='000').status_code, 400)
        self.n.refresh_from_db()
        self.assertEqual(self.n.plan_estado, 'sin_activar')

    def test_con_firma_actualiza_el_plan(self):
        self.assertEqual(self.mandar().status_code, 200)
        self.n.refresh_from_db()
        self.assertEqual((self.n.plan_estado, self.n.stripe_suscripcion), ('prueba', 'sub_123'))
