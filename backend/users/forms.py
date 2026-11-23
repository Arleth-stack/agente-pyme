"""Formulario para entrar al panel con el WhatsApp."""
from django import forms
from django.contrib.auth import authenticate

from core.widgets import Telefono

from .models import solo_digitos


class EntrarForm(forms.Form):
    """WhatsApp de 10 dígitos y contraseña."""

    telefono = forms.CharField(label='Tu WhatsApp (10 dígitos)', widget=Telefono(attrs={'autofocus': True}))
    contrasena = forms.CharField(label='Contraseña', strip=False, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'autocomplete': 'current-password'}))

    error_messages = {
        'faltan': 'Escribe tu WhatsApp y tu contraseña.',
        'incorrectos': 'WhatsApp o contraseña incorrectos.',
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.usuario = None
        super().__init__(*args, **kwargs)

    def clean_telefono(self):
        return solo_digitos(self.cleaned_data['telefono'])

    def clean(self):
        datos = super().clean()
        telefono, clave = datos.get('telefono'), datos.get('contrasena')
        if not telefono or not clave:
            raise forms.ValidationError(self.error_messages['faltan'])
        self.usuario = authenticate(self.request, telefono=telefono, password=clave)
        if self.usuario is None:
            raise forms.ValidationError(self.error_messages['incorrectos'])
        return datos
