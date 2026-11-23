"""Pruebas de la página de inicio."""
from django.test import TestCase

from chat.tests import salon


class InicioTest(TestCase):
    def setUp(self):
        n = salon()
        n.slug, n.nombre, n.es_demo = 'salon-bella', 'Salón Bella', True
        n.save()

    def test_carga_con_sus_secciones(self):
        r = self.client.get('/')
        for texto in ('Tu WhatsApp<br> contesta solo', 'Pruébalo como cliente', 'Y te avisa a ti', 'Así empiezas',
                      'Para quién es', 'La puerta de entrada a Merkatics', '¿Cuánto cuesta?', 'Empieza con<br> tu nombre'):
            self.assertContains(r, texto)

    def test_usa_bootstrap_y_su_tema(self):
        r = self.client.get('/')
        self.assertContains(r, 'bootstrap.min.css')
        self.assertContains(r, 'inicio/css/inicio.css')
        self.assertContains(r, 'offcanvas-lg')
        self.assertContains(r, 'data-bs-spy="scroll"')

    def test_qr_y_enlace_del_negocio_de_ejemplo(self):
        r = self.client.get('/')
        self.assertContains(r, 'data-qr="salon-bella"')
        self.assertIn('<svg', r.content.decode())
        self.assertContains(r, 'testserver/chat/salon-bella')

    def test_enlaces_a_las_demas_pantallas(self):
        r = self.client.get('/')
        for url in ('/crear/', '/cuenta/entrar/', '/demo/', '/chat/salon-bella/'):
            self.assertContains(r, f'href="{url}')
