"""Etiqueta {% icono "nombre" %}: dibuja un icono de Lucide dentro de la página."""
import re
from functools import lru_cache
from pathlib import Path

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()
CARPETA = Path(__file__).resolve().parent.parent / 'static' / 'core' / 'iconos'


@lru_cache(maxsize=128)
def _svg(nombre):
    """Lee el SVG una sola vez y le quita el comentario de licencia y el tamaño fijo."""
    archivo = CARPETA / f'{nombre}.svg'
    if not re.fullmatch(r'[a-z0-9-]+', nombre) or not archivo.exists():
        raise template.TemplateSyntaxError(f'No existe el icono «{nombre}» en core/static/core/iconos/.')
    svg = re.sub(r'<!--.*?-->', '', archivo.read_text(encoding='utf-8'), flags=re.S).strip()
    svg = re.sub(r'\s(width|height|class)="[^"]*"', '', svg, count=3)
    return re.sub(r'\s+', ' ', svg)


@register.simple_tag
def icono(nombre, clase='', tam=20, titulo=''):
    """{% icono "menu" clase="me-2" tam=18 titulo="Abrir menú" %}"""
    atributos = f' width="{int(tam)}" height="{int(tam)}" class="icono {escape(clase)}"'
    if titulo:
        atributos += f' role="img" aria-label="{escape(titulo)}"'
    else:
        atributos += ' aria-hidden="true" focusable="false"'
    return mark_safe(_svg(nombre).replace('<svg', '<svg' + atributos, 1))
