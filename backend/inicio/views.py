"""Página de inicio y demo para presentar."""
from django.shortcuts import render

from negocios.models import Negocio


def inicio(request):
    """Página de inicio."""
    return render(request, 'inicio/inicio.html', {'demos': Negocio.objects.filter(es_demo=True)})


def demo(request):
    """Chat del cliente y panel del dueño lado a lado."""
    return render(request, 'inicio/demo.html', {'demos': Negocio.objects.filter(es_demo=True)})
