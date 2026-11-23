"""Panel del dueño."""
from django.shortcuts import render

from negocios.permisos import con_negocio


@con_negocio()
def inicio(request):
    """Página principal del panel."""
    return render(request, 'panel/inicio.html', {'negocio': request.negocio, 'rol': request.rol})
