"""Widgets de formulario con el estilo de Bootstrap."""
from django import forms


class Telefono(forms.TextInput):
    """WhatsApp de 10 dígitos: en celular abre el teclado de números."""

    def __init__(self, attrs=None):
        base = {'inputmode': 'numeric', 'autocomplete': 'tel', 'maxlength': '14', 'class': 'form-control',
                'placeholder': '55 1234 5678'}
        super().__init__({**base, **(attrs or {})})
