"""Alta del negocio: lo guarda todo o nada."""
import re

from django.db import IntegrityError, transaction

from chat.servicios import normalizar

from .models import GIROS, TEMAS, Miembro, Negocio, Pregunta, horario_valido


class ErrorAlta(ValueError):
    """Dato inválido al crear el negocio; el mensaje es el código del error."""


RESERVADOS = {'enviar', 'mensajes', 'admin', 'panel', 'static', 'media'}


def slug_libre(nombre):
    """Enlace del chat a partir del nombre: «Salón Bella» → salon-bella (sin repetir)."""
    base = re.sub(' ', '-', normalizar(nombre))[:60].strip('-') or 'negocio'
    slug, n = base, 1
    while slug in RESERVADOS or Negocio.objects.filter(slug=slug).exists():
        n += 1
        slug = f'{base}-{n}'
    return slug


def crear_negocio(usuario, datos):
    """Crea negocio, membresía de dueño y preguntas; si la cuenta ya tiene negocio, lo regresa."""
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
            raise ErrorAlta('datos_invalidos:nombre')
        if giro not in dict(GIROS):
            raise ErrorAlta('datos_invalidos:giro')
        if not re.fullmatch(r'[0-9]{10}', telefono):
            raise ErrorAlta('datos_invalidos:telefono')
        if direccion and len(direccion) > 120:
            raise ErrorAlta('datos_invalidos:direccion')
        if not horario_valido(horario):
            raise ErrorAlta('datos_invalidos:horario')
        if not isinstance(preguntas, list) or not 3 <= len(preguntas) <= 60:
            raise ErrorAlta('datos_invalidos:preguntas')

        negocio = Negocio.objects.create(slug=slug_libre(nombre), nombre=nombre, giro=giro, telefono=telefono,
                                         direccion=direccion, horario=horario)
        Miembro.objects.create(negocio=negocio, usuario=usuario, rol='dueno')

        vistas = set()
        for i, p in enumerate(preguntas, 1):
            texto = (p.get('pregunta') or '').strip()
            respuesta = (p.get('respuesta') or '').strip()
            tema = p.get('tema') or 'otros'
            if tema not in dict(TEMAS) or not 3 <= len(texto) <= 150 or not 1 <= len(respuesta) <= 500:
                raise ErrorAlta('datos_invalidos:preguntas')
            if normalizar(texto) in vistas:
                raise ErrorAlta('preguntas_repetidas')
            vistas.add(normalizar(texto))
            try:
                with transaction.atomic():
                    Pregunta.objects.create(negocio=negocio, orden=i, tema=tema, pregunta=texto, respuesta=respuesta,
                                            otras_formas=(p.get('otras_formas') or '').strip() or None)
            except IntegrityError as e:
                raise ErrorAlta('preguntas_repetidas') from e

        return {'slug': negocio.slug, 'nombre': negocio.nombre, 'ya_existia': False}
