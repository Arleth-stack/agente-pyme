"""Pruebas del chat público y de la redacción con inteligencia artificial (F2-03, F2-04, F2-08)."""
from unittest import mock

from django.test import TestCase, override_settings

from negocios.models import Negocio, Pregunta

from core import ia as redaccion

from .models import Aviso, Conversacion
from .servicios import buscar_pregunta, detectar_motivo, normalizar, similitud

HORARIO = {d: {'abre': '00:00', 'cierra': '23:59'} for d in ('lun', 'mar', 'mie', 'jue', 'vie', 'sab', 'dom')}


def salon():
    n = Negocio.objects.create(slug='salon-prueba', nombre='Salón Prueba', giro='salon', telefono='5512345678',
                               horario=HORARIO)
    Pregunta.objects.create(negocio=n, orden=1, tema='precios', pregunta='¿Cuánto cuesta el corte de dama?',
                            otras_formas='precio del corte, corte mujer', respuesta='El corte de dama cuesta $250.')
    Pregunta.objects.create(negocio=n, orden=2, tema='citas', pregunta='¿Necesito cita?',
                            respuesta='No es necesaria, pero con cita no esperas.')
    Pregunta.objects.create(negocio=n, orden=3, tema='pagos', pregunta='¿Aceptan tarjeta?',
                            respuesta='Sí, aceptamos tarjeta y efectivo.')
    return n


class TextoTest(TestCase):
    def test_normalizar(self):
        self.assertEqual(normalizar('¿Cuánto CUESTA el Niño?'), 'cuanto cuesta el nino')

    def test_similitud_como_pg_trgm(self):
        self.assertEqual(similitud('corte', 'corte'), 1.0)
        self.assertGreater(similitud('manicure', 'manicur'), 0.5)

    def test_motivos(self):
        self.assertEqual(detectar_motivo('me duele mucho'), 'queja_o_urgencia')
        self.assertEqual(detectar_motivo('quiero hablar con alguien'), 'pidio_persona')
        self.assertEqual(detectar_motivo('quiero cita el sábado a las 11'), 'pide_cita')
        self.assertIsNone(detectar_motivo('¿necesito cita?'))

    def test_buscar_pregunta(self):
        n = salon()
        self.assertEqual(buscar_pregunta(n, 'cuanto cobran por el corte de mujer').tema, 'precios')
        self.assertIsNone(buscar_pregunta(n, '¿hacen extensiones de pestañas?'))


class ChatPublicoTest(TestCase):
    def setUp(self):
        self.n = salon()
        self.token = self.client.post(f'/chat/{self.n.slug}/iniciar/').json()['token']

    def enviar(self, texto):
        return self.client.post('/chat/enviar/', {'token': self.token, 'texto': texto},
                                content_type='application/json').json()

    def test_estado_del_negocio(self):
        r = self.client.get(f'/chat/{self.n.slug}/estado/').json()
        self.assertEqual(r['nombre'], 'Salón Prueba')
        self.assertIn('Pregúntame por', r['bienvenida'])

    def test_contesta_con_el_texto_del_dueno(self):
        cliente, respuesta = self.enviar('cuanto cuesta el corte de dama?')
        self.assertEqual(respuesta['texto'], 'El corte de dama cuesta $250.')
        self.assertEqual(respuesta['tipo'], 'faq')

    def test_si_no_sabe_avisa_y_ofrece_opciones(self):
        _, r = self.enviar('¿hacen extensiones de pestañas?')
        self.assertEqual(r['motivo'], 'no_la_sabe')
        self.assertTrue(r['opciones'])
        conv = Conversacion.objects.get(token=self.token)
        self.assertEqual(conv.estado, 'te_necesita')
        # Elegir de la lista con el número.
        _, r2 = self.enviar('1')
        self.assertEqual(r2['tipo'], 'faq')

    def test_un_solo_aviso_y_sube_de_prioridad(self):
        self.enviar('¿hacen extensiones?')
        self.enviar('me dejaron mal el corte, estoy molesta')
        avisos = Aviso.objects.filter(conversacion__token=self.token, estado='pendiente')
        self.assertEqual(avisos.count(), 1)
        self.assertEqual(avisos.get().motivo, 'queja_o_urgencia')

    def test_token_inventado(self):
        r = self.client.post('/chat/enviar/', {'token': '00000000-0000-0000-0000-000000000000', 'texto': 'hola'},
                             content_type='application/json')
        self.assertEqual(r.status_code, 404)


def error_gemini(codigo):
    from google.genai import errors
    return errors.APIError(codigo, {'error': {'code': codigo, 'message': 'simulado'}})


@override_settings(GEMINI_API_KEY='llave-de-prueba')
class RedaccionTest(TestCase):
    def setUp(self):
        self.n = salon()
        self.d = {'tipo': 'faq', 'texto': 'El corte de dama cuesta $250.'}

    def test_red_de_seguridad(self):
        self.assertTrue(redaccion.es_segura('Cuesta $250.', '¡Claro! El corte de dama te sale en $250.',
                                            'cuanto cuesta el corte de dama'))
        self.assertFalse(redaccion.es_segura('Cuesta $250.', 'Cuesta $200.'))           # cambió el precio
        self.assertFalse(redaccion.es_segura('Cuesta $250.', 'Cuesta $250 y el tinte $600.'))  # agregó un dato
        self.assertFalse(redaccion.es_segura('Cuesta $250.', 'Soy un bot: cuesta $250.'))      # palabra prohibida
        self.assertTrue(redaccion.es_segura('Desde $1,100.', 'Va desde $1100.'))
        # Sin números, pero agrega una invitación que el dueño no escribió.
        self.assertFalse(redaccion.es_segura('El corte de dama cuesta $250.',
                                             'El corte de dama cuesta $250. Quedo a tus órdenes por si gustas agendar tu cita.'))
        self.assertTrue(redaccion.es_segura('Sí, la keratina va desde $1,500 según el largo del cabello.',
                                            'Hola, sí hacemos keratina. El costo va desde $1,500 según el largo de tu cabello.',
                                            'hacen keratina?'))

    @mock.patch('core.ia._pedir')
    def test_usa_la_redaccion_si_es_segura(self, post):
        post.return_value = '¡Hola! El corte de dama te cuesta $250.'
        self.assertEqual(redaccion.redactar(self.n, 'cuanto el corte', self.d), '¡Hola! El corte de dama te cuesta $250.')

    @mock.patch('core.ia._pedir')
    def test_si_inventa_se_usa_el_texto_exacto(self, post):
        post.return_value = 'El corte cuesta $250 y hoy hay 2x1.'
        self.assertIsNone(redaccion.redactar(self.n, 'cuanto el corte', self.d))

    @mock.patch('core.ia._pedir')
    def test_si_se_acaba_la_capa_gratis(self, post):
        post.side_effect = error_gemini(429)
        self.assertIsNone(redaccion.redactar(self.n, 'cuanto el corte', self.d))
        self.assertEqual(post.call_count, 1)  # con 429 no insiste con otros modelos

    @mock.patch('core.ia._pedir')
    def test_si_un_modelo_esta_saturado_usa_el_siguiente(self, post):
        post.side_effect = [error_gemini(503), 'Claro, el corte de dama cuesta $250.']
        self.assertEqual(redaccion.redactar(self.n, 'cuanto el corte de dama', self.d),
                         'Claro, el corte de dama cuesta $250.')

    @mock.patch('core.ia._pedir')
    def test_no_redacta_avisos_ni_si_el_dueno_la_apago(self, post):
        self.assertIsNone(redaccion.redactar(self.n, 'x', {'tipo': 'aviso', 'texto': 'Ya le avisé al equipo.'}))
        self.n.redaccion_activa = False
        self.assertIsNone(redaccion.redactar(self.n, 'x', self.d))
        post.assert_not_called()

    @override_settings(GEMINI_API_KEY='')
    def test_sin_llave_no_pasa_nada(self):
        self.assertIsNone(redaccion.redactar(self.n, 'x', self.d))

    @mock.patch('core.ia._pedir')
    def test_en_el_chat_queda_guardado_el_original(self, post):
        post.return_value = 'Claro, el corte de dama cuesta $250.'
        token = self.client.post(f'/chat/{self.n.slug}/iniciar/').json()['token']
        r = self.client.post('/chat/enviar/', {'token': token, 'texto': 'cuanto el corte de dama'},
                             content_type='application/json').json()
        self.assertEqual(r[1]['texto'], 'Claro, el corte de dama cuesta $250.')
        conv = Conversacion.objects.get(token=token)
        self.assertEqual(conv.mensajes.get(autor='asistente').texto_original, 'El corte de dama cuesta $250.')
