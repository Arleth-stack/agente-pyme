"""Entrar y salir del panel."""
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import EntrarForm


def entrar(request):
    """Entra con el WhatsApp; si ya hay sesión, va directo al panel."""
    if request.user.is_authenticated:
        return redirect('panel:inicio')
    form = EntrarForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.usuario)
        return redirect(request.GET.get('next') or 'panel:inicio')
    return render(request, 'users/entrar.html', {'form': form})


@require_POST
def salir(request):
    """Cierra la sesión."""
    logout(request)
    return redirect('users:entrar')
