"""Alta del negocio («Crea tu negocio»)."""
from django.shortcuts import render


def crear(request):
    """Formulario de 5 pasos para crear el negocio."""
    return render(request, 'negocios/crear.html')
