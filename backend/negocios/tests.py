"""Pruebas del alta del negocio y del aislamiento entre negocios."""
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import TestCase

from chat.models import Aviso, Conversacion, Mensaje

from .models import Miembro, Negocio, Pregunta
from .permisos import negocio_de
from .servicios import ErrorAlta, crear_negocio, slug_libre

Usuario = get_user_model()
HORARIO = {d: {'abre': '09:00', 'cierra': '19:00'} for d in ('lun', 'mar', 'mie', 'jue', 'vie', 'sab')} | {'dom': None}


def negocio_con_dueno(nombre, telefono, rol='dueno'):
    """Negocio con su cuenta, una pregunta y una conversación con aviso."""
    n = Negocio.objects.create(slug=slug_libre(nombre), nombre=nombre, giro='salon', telefono=telefono, horario=HORARIO)
    u = Usuario.objects.create_user(telefono, 'clave-segura-1')
    Miembro.objects.create(negocio=n, usuario=u, rol=rol)
    Pregunta.objects.create(negocio=n, tema='precios', pregunta='¿Cuánto cuesta el corte?', respuesta='El corte cuesta $150.')
    c = Conversacion.objects.create(negocio=n, cliente_nombre='Cliente de ' + nombre)
    Mensaje.objects.create(conversacion=c, autor='cliente', texto='hola')
    Aviso.objects.create(conversacion=c, motivo='no_la_sabe', mensaje_cliente='hola')
    return n, u, c


class AislamientoTest(TestCase):
    """Una cuenta solo obtiene su propio negocio."""

    def test_cada_cuenta_su_negocio(self):
        a, ua, _ = negocio_con_dueno('Salon A', '5511110001')
        b, ub, _ = negocio_con_dueno('Salon B', '5511110002')
        self.assertEqual(negocio_de(ua), a)
        self.assertEqual(negocio_de(ub), b)

    def test_sin_negocio_no_hay_panel(self):
        u = Usuario.objects.create_user('5511110003', 'clave-segura-1')
        with self.assertRaises(PermissionDenied):
            negocio_de(u)

    def test_encargado_no_es_dueno(self):
        _, u, _ = negocio_con_dueno('Salon C', '5511110004', rol='encargado')
        self.assertTrue(negocio_de(u))
        with self.assertRaises(PermissionDenied):
            negocio_de(u, solo_dueno=True)


class AltaTest(TestCase):
    datos = {'nombre': 'Estética Lupita', 'giro': 'salon', 'telefono': '55 1234 5678', 'horario': HORARIO,
             'preguntas': [{'tema': 'precios', 'pregunta': '¿Cuánto cuesta el corte?', 'respuesta': '$150'},
                           {'tema': 'horarios', 'pregunta': '¿A qué hora abren?', 'respuesta': 'A las 9.'},
                           {'tema': 'citas', 'pregunta': '¿Necesito cita?', 'respuesta': 'No.'}]}

    def setUp(self):
        self.u = Usuario.objects.create_user('5512345678', 'clave-segura-1')

    def test_crea_y_no_duplica(self):
        r = crear_negocio(self.u, self.datos)
        self.assertEqual(r, {'slug': 'estetica-lupita', 'nombre': 'Estética Lupita', 'ya_existia': False})
        self.assertEqual(Negocio.objects.get(slug='estetica-lupita').preguntas.count(), 3)
        self.assertTrue(crear_negocio(self.u, self.datos)['ya_existia'])
        self.assertEqual(Negocio.objects.count(), 1)

    def test_preguntas_repetidas_no_guardan_nada(self):
        datos = {**self.datos, 'preguntas': self.datos['preguntas'] + [
            {'tema': 'precios', 'pregunta': '¿cuanto cuesta el corte?', 'respuesta': 'otra'}]}
        with self.assertRaises(ErrorAlta):
            crear_negocio(self.u, datos)
        self.assertEqual(Negocio.objects.count(), 0)

    def test_enlace_reservado(self):
        Negocio.objects.create(slug='salon-bella', nombre='Salón Bella', giro='salon', telefono='5500000000',
                               horario=HORARIO)
        self.assertEqual(slug_libre('Salón Bella'), 'salon-bella-2')
        self.assertEqual(slug_libre('Enviar'), 'enviar-2')
