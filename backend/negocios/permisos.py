"""Quién puede ver o cambiar qué. Toda pantalla del panel obtiene su negocio aquí,
así una cuenta nunca ve ni cambia datos de otro negocio."""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from .models import Miembro


def membresia(usuario):
    """La membresía de la cuenta (un negocio por cuenta) o None."""
    if not usuario.is_authenticated:
        return None
    return Miembro.objects.select_related('negocio').filter(usuario=usuario).first()


def negocio_de(usuario, solo_dueno=False):
    """El negocio de la cuenta; si no tiene, o si se pide dueño y es encargado, lanza PermissionDenied."""
    m = membresia(usuario)
    if m is None:
        raise PermissionDenied('sin_negocio')
    if solo_dueno and m.rol != 'dueno':
        raise PermissionDenied('solo_dueno')
    return m.negocio


def con_negocio(solo_dueno=False):
    """Decorador de vistas: pide sesión y pasa `negocio` y `rol`; sin negocio manda a crearlo."""
    def decorador(vista):
        @login_required
        @wraps(vista)
        def envuelta(request, *args, **kwargs):
            m = membresia(request.user)
            if m is None:
                return redirect('negocios:crear')
            if solo_dueno and m.rol != 'dueno':
                raise PermissionDenied('solo_dueno')
            request.negocio, request.rol = m.negocio, m.rol
            return vista(request, *args, **kwargs)
        return envuelta
    return decorador


def es_dueno(usuario, negocio):
    """¿La cuenta es dueña de ese negocio?"""
    return Miembro.objects.filter(usuario=usuario, negocio=negocio, rol='dueno').exists()
