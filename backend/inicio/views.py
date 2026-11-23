"""Página de inicio y demo para presentar."""
from django.shortcuts import render
from django.urls import reverse

from negocios.models import Negocio

from .servicios import qr_svg

SLUG_INICIAL = 'salon-bella'


def _demos(request):
    """Los negocios de ejemplo con el enlace y el QR de su chat."""
    demos = []
    for n in Negocio.objects.filter(es_demo=True).order_by('nombre'):
        url = request.build_absolute_uri(reverse('chat:pantalla', args=[n.slug]))
        demos.append({'negocio': n, 'url': url, 'qr': qr_svg(url)})
    return demos


def inicio(request):
    """Página de inicio."""
    demos = _demos(request)
    elegido = next((d for d in demos if d['negocio'].slug == SLUG_INICIAL), demos[0] if demos else None)
    enlace = request.build_absolute_uri(reverse('chat:pantalla', args=[SLUG_INICIAL]))
    return render(request, 'inicio/inicio.html', {
        'demos': demos,
        'elegido': elegido,
        'enlace_ejemplo': enlace,
        'enlace_ejemplo_corto': enlace.split('://', 1)[-1].rstrip('/'),
    })


def demo(request):
    """Chat del cliente y panel del dueño lado a lado."""
    return render(request, 'inicio/demo.html', {'demos': _demos(request)})
