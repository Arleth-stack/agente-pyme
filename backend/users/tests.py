"""Pruebas de entrar con el WhatsApp."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

Usuario = get_user_model()


class EntrarTest(TestCase):
    def setUp(self):
        Usuario.objects.create_user('55 1234 5678', 'clave-segura-1')

    def test_entra_con_su_whatsapp(self):
        r = self.client.post(reverse('users:entrar'), {'telefono': '55-1234-5678', 'contrasena': 'clave-segura-1'})
        self.assertRedirects(r, reverse('panel:inicio'), fetch_redirect_response=False)

    def test_contrasena_equivocada(self):
        r = self.client.post(reverse('users:entrar'), {'telefono': '5512345678', 'contrasena': 'otra-clave'})
        self.assertContains(r, 'WhatsApp o contraseña incorrectos.')

    def test_el_numero_debe_tener_10_digitos(self):
        with self.assertRaises(ValueError):
            Usuario.objects.create_user('12345', 'clave-segura-1')
