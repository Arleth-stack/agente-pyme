"""Reglas de negocio que no dependen de la pantalla: alta del negocio y a quién pertenece cada cuenta."""
import re

from django.db import IntegrityError, transaction
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from chat.motor import normalizar

from .models import GIROS, TEMAS, Miembro, Negocio, Pregunta, horario_valido


def membresia(usuario):
    """La membresía de la cuenta (un negocio por cuenta, como en la Fase 1)."""
    m = Miembro.objects.select_related('negocio').filter(usuario=usuario).first()
    if m is None:
        raise NotFound('sin_negocio')
    return m


def negocio_de(usuario, solo_dueno=False):
    """El negocio de la cuenta. TODA consulta del panel parte de aquí: así una
    cuenta nunca ve ni cambia datos de otro negocio (el aislamiento de la Fase 2)."""
    m = membresia(usuario)
    if solo_dueno and m.rol != 'dueno':
        raise PermissionDenied('solo_dueno')
    return m.negocio


def slug_libre(nombre):
    base = re.sub(' ', '-', normalizar(nombre))[:60].strip('-') or 'negocio'
    slug, n = base, 1
    while Negocio.objects.filter(slug=slug).exists():
        n += 1
        slug = f'{base}-{n}'
    return slug


def crear_negocio(usuario, datos):
    """Igual que public.crear_negocio: todo o nada, y si la cuenta ya tiene negocio lo regresa."""
    with transaction.atomic():
        # Un alta a la vez por cuenta (doble clic o reintento).
        type(usuario).objects.select_for_update().get(pk=usuario.pk)
        existente = Miembro.objects.select_related('negocio').filter(usuario=usuario).first()
        if existente:
            n = existente.negocio
            return {'slug': n.slug, 'nombre': n.nombre, 'ya_existia': True}

        nombre = (datos.get('nombre') or '').strip()
        giro = datos.get('giro')
        telefono = re.sub(r'\D', '', datos.get('telefono') or '')
        direccion = (datos.get('direccion') or '').strip() or None
        horario = datos.get('horario')
        preguntas = datos.get('preguntas') or []

        if not 2 <= len(nombre) <= 60:
            raise ValidationError('datos_invalidos:nombre')
        if giro not in dict(GIROS):
            raise ValidationError('datos_invalidos:giro')
        if not re.fullmatch(r'[0-9]{10}', telefono):
            raise ValidationError('datos_invalidos:telefono')
        if direccion and len(direccion) > 120:
            raise ValidationError('datos_invalidos:direccion')
        if not horario_valido(horario):
            raise ValidationError('datos_invalidos:horario')
        if not isinstance(preguntas, list) or not 3 <= len(preguntas) <= 60:
            raise ValidationError('datos_invalidos:preguntas')

        negocio = Negocio.objects.create(slug=slug_libre(nombre), nombre=nombre, giro=giro, telefono=telefono,
                                         direccion=direccion, horario=horario)
        Miembro.objects.create(negocio=negocio, usuario=usuario, rol='dueno')

        vistas = set()
        for i, p in enumerate(preguntas, 1):
            texto = (p.get('pregunta') or '').strip()
            respuesta = (p.get('respuesta') or '').strip()
            tema = p.get('tema') or 'otros'
            if tema not in dict(TEMAS) or not 3 <= len(texto) <= 150 or not 1 <= len(respuesta) <= 500:
                raise ValidationError('datos_invalidos:preguntas')
            if normalizar(texto) in vistas:
                raise ValidationError('preguntas_repetidas')
            vistas.add(normalizar(texto))
            try:
                with transaction.atomic():
                    Pregunta.objects.create(negocio=negocio, orden=i, tema=tema, pregunta=texto, respuesta=respuesta,
                                            otras_formas=(p.get('otras_formas') or '').strip() or None)
            except IntegrityError as e:
                raise ValidationError('preguntas_repetidas') from e

        return {'slug': negocio.slug, 'nombre': negocio.nombre, 'ya_existia': False}
