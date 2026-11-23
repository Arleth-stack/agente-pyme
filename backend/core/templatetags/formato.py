"""Filtros de formato para las plantillas."""
import markdown as md
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def telefono(valor):
    """5512345678 → 55 1234 5678."""
    t = ''.join(c for c in str(valor or '') if c.isdigit())
    return f'{t[:2]} {t[2:6]} {t[6:]}' if len(t) == 10 else valor


@register.filter
def markdown(texto):
    """Textos largos con formato sencillo (negritas, listas, enlaces), sin HTML suelto."""
    return mark_safe(md.markdown(escape(texto or ''), extensions=['sane_lists']))
