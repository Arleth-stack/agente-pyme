"""Pruebas de lo común: iconos, filtros y plantilla base."""
from django.template import Context, Template, TemplateSyntaxError
from django.test import TestCase


class IconoTest(TestCase):
    def test_dibuja_el_icono(self):
        html = Template('{% load icono %}{% icono "menu" clase="me-2" tam=18 %}').render(Context())
        self.assertIn('<svg width="18" height="18" class="icono me-2"', html)
        self.assertIn('aria-hidden="true"', html)
        self.assertNotIn('<!--', html)

    def test_icono_con_titulo_se_lee(self):
        html = Template('{% load icono %}{% icono "menu" titulo="Abrir menú" %}').render(Context())
        self.assertIn('aria-label="Abrir menú"', html)

    def test_icono_que_no_existe(self):
        with self.assertRaises(TemplateSyntaxError):
            Template('{% load icono %}{% icono "no-existe" %}').render(Context())


class FormatoTest(TestCase):
    def test_telefono(self):
        self.assertEqual(Template('{% load formato %}{{ t|telefono }}').render(Context({'t': '5512345678'})), '55 1234 5678')


class BaseTest(TestCase):
    def test_pantalla_entrar_usa_el_tema(self):
        r = self.client.get('/cuenta/entrar/')
        self.assertContains(r, 'core/css/tema.css')
        self.assertContains(r, 'bootstrap.min.css')
        self.assertContains(r, 'Entra a tu panel')
