"""Datos que todas las plantillas tienen a la mano."""
from django.conf import settings


def sitio(request):
    """Nombre del producto y dirección pública del sitio."""
    return {
        'NOMBRE_PRODUCTO': 'Tu WhatsApp contesta solo',
        'SITIO_URL': settings.SITIO_URL,
    }
