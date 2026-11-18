"""Pruebas de cuentas, alta del negocio y AISLAMIENTO entre negocios (F2-02, F2-04)."""
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from chat.models import Aviso, Conversacion, Mensaje

from .models import Miembro, Negocio, Pregunta

User = get_user_model()
HORARIO = {d: {'abre': '09:00', 'cierra': '19:00'} for d in ('lun', 'mar', 'mie', 'jue', 'vie', 'sab')} | {'dom': None}


def negocio_con_dueno(nombre, correo, rol='dueno'):
    n = Negocio.objects.create(slug=nombre.lower().replace(' ', '-'), nombre=nombre, giro='salon',
                               telefono='5512345678', horario=HORARIO)
    u = User.objects.create_user(username=correo, email=correo, password='clave-segura-1')
    Miembro.objects.create(negocio=n, usuario=u, rol=rol)
    Pregunta.objects.create(negocio=n, tema='precios', pregunta='¿Cuánto cuesta el corte?', respuesta='El corte cuesta $150.')
    c = Conversacion.objects.create(negocio=n, cliente_nombre='Cliente de ' + nombre)
    Mensaje.objects.create(conversacion=c, autor='cliente', texto='hola')
    Aviso.objects.create(conversacion=c, motivo='no_la_sabe', mensaje_cliente='hola')
    return n, u, c


class AislamientoTest(APITestCase):
    """Una cuenta NUNCA puede leer ni cambiar nada de otro negocio."""

    def setUp(self):
        self.a, self.ua, self.ca = negocio_con_dueno('Salon A', 'a@ejemplo.com')
        self.b, self.ub, self.cb = negocio_con_dueno('Salon B', 'b@ejemplo.com')
        self.client.force_authenticate(self.ua)

    def test_solo_ve_sus_conversaciones(self):
        r = self.client.get('/api/panel/conversaciones')
        self.assertEqual([c['id'] for c in r.json()], [str(self.ca.id)])

    def test_no_abre_conversacion_ajena(self):
        self.assertEqual(self.client.get(f'/api/panel/conversaciones/{self.cb.id}').status_code, 404)

    def test_no_contesta_ni_resuelve_conversacion_ajena(self):
        self.assertEqual(self.client.post(f'/api/panel/conversaciones/{self.cb.id}/responder',
                                          {'texto': 'hackeo'}, format='json').status_code, 404)
        self.assertEqual(self.client.post(f'/api/panel/conversaciones/{self.cb.id}/resolver').status_code, 404)
        self.assertFalse(Mensaje.objects.filter(conversacion=self.cb, autor='dueno').exists())
        self.assertTrue(Aviso.objects.filter(conversacion=self.cb, estado='pendiente').exists())

    def test_no_cambia_ni_borra_preguntas_ajenas(self):
        p = self.b.preguntas.first()
        self.assertEqual(self.client.patch(f'/api/panel/preguntas/{p.id}', {'respuesta': 'gratis'},
                                           format='json').status_code, 404)
        self.assertEqual(self.client.delete(f'/api/panel/preguntas/{p.id}').status_code, 404)
        p.refresh_from_db()
        self.assertEqual(p.respuesta, 'El corte cuesta $150.')

    def test_solo_lista_sus_preguntas(self):
        r = self.client.get('/api/panel/preguntas')
        self.assertEqual(len(r.json()), 1)
        self.assertEqual(Pregunta.objects.get(id=r.json()[0]['id']).negocio, self.a)

    def test_no_puede_cambiar_su_plan(self):
        self.client.patch('/api/panel/negocio', {'plan_estado': 'activa', 'es_demo': True}, format='json')
        self.a.refresh_from_db()
        self.assertEqual(self.a.plan_estado, 'sin_activar')
        self.assertFalse(self.a.es_demo)

    def test_sin_sesion_no_hay_panel(self):
        self.client.force_authenticate(None)
        self.assertIn(self.client.get('/api/panel/conversaciones').status_code, (401, 403))


class EncargadoTest(APITestCase):
    def test_encargado_ve_pero_no_cambia_preguntas(self):
        n, u, _ = negocio_con_dueno('Salon C', 'c@ejemplo.com', rol='encargado')
        self.client.force_authenticate(u)
        self.assertEqual(self.client.get('/api/panel/conversaciones').status_code, 200)
        self.assertEqual(self.client.post('/api/panel/preguntas', {'tema': 'otros', 'pregunta': '¿Hay estacionamiento?',
                                                                   'respuesta': 'Sí.'}, format='json').status_code, 403)
        self.assertEqual(self.client.patch('/api/panel/negocio', {'nombre': 'Otro'}, format='json').status_code, 403)


class AltaTest(APITestCase):
    datos = {'nombre': 'Estética Lupita', 'giro': 'salon', 'telefono': '55 1234 5678', 'horario': HORARIO,
             'preguntas': [{'tema': 'precios', 'pregunta': '¿Cuánto cuesta el corte?', 'respuesta': '$150'},
                           {'tema': 'horarios', 'pregunta': '¿A qué hora abren?', 'respuesta': 'A las 9.'},
                           {'tema': 'citas', 'pregunta': '¿Necesito cita?', 'respuesta': 'No.'}]}

    def test_registro_crear_y_yo(self):
        r = self.client.post('/api/cuentas/registro', {'correo': 'Lupita@Ejemplo.com', 'contrasena': 'clave-segura-1'},
                             format='json')
        self.assertEqual(r.status_code, 201)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + r.json()['token'])
        r = self.client.post('/api/negocios/crear', self.datos, format='json')
        self.assertEqual(r.json(), {'slug': 'estetica-lupita', 'nombre': 'Estética Lupita', 'ya_existia': False})
        yo = self.client.get('/api/cuentas/yo').json()
        self.assertEqual(yo['negocio']['slug'], 'estetica-lupita')
        self.assertEqual(Negocio.objects.get(slug='estetica-lupita').preguntas.count(), 3)
        # Reintento (doble clic): no crea otro negocio.
        r = self.client.post('/api/negocios/crear', self.datos, format='json')
        self.assertTrue(r.json()['ya_existia'])
        self.assertEqual(Negocio.objects.count(), 1)

    def test_preguntas_repetidas_no_guardan_nada(self):
        u = User.objects.create_user(username='x@ejemplo.com', password='clave-segura-1')
        self.client.force_authenticate(u)
        datos = {**self.datos, 'preguntas': self.datos['preguntas'] + [
            {'tema': 'precios', 'pregunta': '¿cuanto cuesta el corte?', 'respuesta': 'otra'}]}
        r = self.client.post('/api/negocios/crear', datos, format='json')
        self.assertEqual(r.json()['error'], 'preguntas_repetidas')
        self.assertEqual(Negocio.objects.count(), 0)

    def test_entrar_con_contrasena_equivocada(self):
        User.objects.create_user(username='y@ejemplo.com', password='clave-segura-1')
        r = self.client.post('/api/cuentas/entrar', {'correo': 'y@ejemplo.com', 'contrasena': 'otra-clave'}, format='json')
        self.assertEqual(r.status_code, 400)


class StripeTest(APITestCase):
    """F2-07 sin llamar a Stripe de verdad."""

    def setUp(self):
        self.n, self.u, _ = negocio_con_dueno('Salon D', 'd@ejemplo.com')
        self.client.force_authenticate(self.u)

    def test_aviso_de_stripe_con_firma_actualiza_el_plan(self):
        import hashlib
        import hmac
        import json
        import time
        from django.test import override_settings
        evento = {'type': 'customer.subscription.updated', 'data': {'object': {
            'id': 'sub_123', 'status': 'trialing', 'customer': 'cus_1', 'trial_end': int(time.time()) + 7 * 86400,
            'cancel_at': None, 'metadata': {'negocio_id': str(self.n.id)}}}}
        crudo = json.dumps(evento).encode()
        t = str(int(time.time()))
        with override_settings(STRIPE_WEBHOOK_SECRET='whsec_prueba'):
            firma = hmac.new(b'whsec_prueba', f'{t}.'.encode() + crudo, hashlib.sha256).hexdigest()
            malo = self.client.post('/api/stripe-aviso', crudo, content_type='application/json',
                                    HTTP_STRIPE_SIGNATURE=f't={t},v1=000')
            self.assertEqual(malo.status_code, 400)
            r = self.client.post('/api/stripe-aviso', crudo, content_type='application/json',
                                 HTTP_STRIPE_SIGNATURE=f't={t},v1={firma}')
        self.assertEqual(r.status_code, 200)
        self.n.refresh_from_db()
        self.assertEqual((self.n.plan_estado, self.n.stripe_suscripcion), ('prueba', 'sub_123'))

    def test_demo_no_paga(self):
        Negocio.objects.filter(id=self.n.id).update(es_demo=True)
        self.assertEqual(self.client.post('/api/panel/plan/prueba').status_code, 400)
