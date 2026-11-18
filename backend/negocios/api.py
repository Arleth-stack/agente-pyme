"""API de cuentas, alta del negocio y panel del dueño.

Regla de aislamiento: cada vista obtiene el negocio con `negocio_de(request.user)`
y SOLO consulta objetos de ese negocio. La prueba `test_aislamiento` lo comprueba.
"""
from datetime import timedelta

from django.contrib.auth import authenticate, get_user_model
from django.db import IntegrityError, transaction
from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from chat.models import Aviso, Conversacion, Mensaje

from .models import TEMAS, Miembro, Pregunta, horario_valido, telefono_10
from .servicios import crear_negocio, membresia, negocio_de

User = get_user_model()


class LimiteEntrar(AnonRateThrottle):
    rate = '10/min'


def _token(usuario):
    return Token.objects.get_or_create(user=usuario)[0].key


# --- Cuentas --------------------------------------------------------------

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
@throttle_classes([LimiteEntrar])
def registro(request):
    """Crea la cuenta; si ya existía con la misma contraseña, entra (como en la Fase 1)."""
    correo = (request.data.get('correo') or '').strip().lower()
    clave = request.data.get('contrasena') or ''
    if '@' not in correo or len(correo) > 120:
        return Response({'error': 'correo_invalido'}, status=400)
    if len(clave) < 8:
        return Response({'error': 'contrasena_corta'}, status=400)
    existente = User.objects.filter(username=correo).first()
    if existente:
        usuario = authenticate(username=correo, password=clave)
        if usuario is None:
            return Response({'error': 'correo_usado'}, status=409)
        return Response({'token': _token(usuario)})
    usuario = User.objects.create_user(username=correo, email=correo, password=clave)
    return Response({'token': _token(usuario)}, status=201)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
@throttle_classes([LimiteEntrar])
def entrar(request):
    correo = (request.data.get('correo') or '').strip().lower()
    usuario = authenticate(username=correo, password=request.data.get('contrasena') or '')
    if usuario is None:
        return Response({'error': 'incorrectos'}, status=400)
    usuario.last_login = timezone.now()
    usuario.save(update_fields=['last_login'])
    return Response({'token': _token(usuario)})


@api_view(['POST'])
def salir(request):
    Token.objects.filter(user=request.user).delete()
    return Response(status=204)


@api_view(['GET'])
def yo(request):
    m = Miembro.objects.select_related('negocio').filter(usuario=request.user).first()
    datos = {'correo': request.user.email, 'negocio': None}
    if m:
        n = m.negocio
        datos['negocio'] = {'id': str(n.id), 'slug': n.slug, 'nombre': n.nombre, 'es_demo': n.es_demo, 'rol': m.rol}
    return Response(datos)


# --- Alta del negocio -----------------------------------------------------

@api_view(['POST'])
def crear(request):
    try:
        return Response(crear_negocio(request.user, request.data))
    except ValidationError as e:
        detalle = e.detail[0] if isinstance(e.detail, list) else e.detail
        return Response({'error': str(detalle)}, status=400)


# --- Mi negocio -----------------------------------------------------------

def _negocio_json(n, rol):
    return {
        'id': str(n.id), 'slug': n.slug, 'nombre': n.nombre, 'giro': n.giro, 'telefono': n.telefono,
        'direccion': n.direccion, 'horario': n.horario, 'zona_horaria': n.zona_horaria, 'es_demo': n.es_demo,
        'rol': rol, 'redaccion_activa': n.redaccion_activa,
        'plan': {'estado': n.plan_estado, 'prueba_termina': n.prueba_termina, 'plan_termina': n.plan_termina,
                 'puede_probar': not n.stripe_suscripcion, 'puede_administrar': bool(n.stripe_cliente)},
    }


@api_view(['GET', 'PATCH'])
def mi_negocio(request):
    m = membresia(request.user)
    n = m.negocio
    if request.method == 'GET':
        return Response(_negocio_json(n, m.rol))
    if m.rol != 'dueno':
        return Response({'error': 'solo_dueno'}, status=403)
    d = request.data
    # Solo estos campos: el plan y lo interno no se pueden cambiar desde aquí.
    if 'nombre' in d:
        nombre = (d['nombre'] or '').strip()
        if not 2 <= len(nombre) <= 60:
            return Response({'error': 'nombre'}, status=400)
        n.nombre = nombre
    if 'telefono' in d:
        tel = ''.join(c for c in str(d['telefono'] or '') if c.isdigit())
        if len(tel) != 10:
            return Response({'error': 'telefono'}, status=400)
        n.telefono = tel
    if 'direccion' in d:
        dir_ = (d['direccion'] or '').strip() or None
        if dir_ and len(dir_) > 120:
            return Response({'error': 'direccion'}, status=400)
        n.direccion = dir_
    if 'horario' in d:
        if not horario_valido(d['horario']):
            return Response({'error': 'horario'}, status=400)
        n.horario = d['horario']
    if 'redaccion_activa' in d:
        n.redaccion_activa = bool(d['redaccion_activa'])
    n.save()
    return Response(_negocio_json(n, m.rol))


# --- Conversaciones -------------------------------------------------------

def _resumen_conv(c):
    ultimo = c.ultimos[0] if c.ultimos else None
    return {
        'id': str(c.id), 'estado': c.estado, 'canal': c.canal, 'cliente_nombre': c.cliente_nombre,
        'ultimo_mensaje_en': c.ultimo_mensaje_en.isoformat(),
        'mensajes': [{'id': ultimo.id, 'texto': ultimo.texto, 'autor': ultimo.autor}] if ultimo else [],
        'avisos': [{'motivo': a.motivo, 'estado': a.estado, 'mensaje_cliente': a.mensaje_cliente} for a in c.avisos.all()],
    }


@api_view(['GET'])
def conversaciones(request):
    n = negocio_de(request.user)
    qs = (Conversacion.objects.filter(negocio=n).order_by('-ultimo_mensaje_en')
          .prefetch_related('avisos', Prefetch('mensajes', queryset=Mensaje.objects.order_by('-id'), to_attr='todos')))
    datos = []
    for c in qs:
        c.ultimos = c.todos[:1]
        datos.append(_resumen_conv(c))
    return Response(datos)


@api_view(['GET'])
def conversacion(request, pk):
    n = negocio_de(request.user)
    c = get_object_or_404(Conversacion, pk=pk, negocio=n)
    despues = int(request.GET.get('despues_de') or 0)
    return Response({
        'id': str(c.id), 'estado': c.estado, 'canal': c.canal, 'cliente_nombre': c.cliente_nombre,
        'cliente_telefono': c.cliente_telefono, 'interes': c.interes,
        'avisos': [{'motivo': a.motivo, 'estado': a.estado, 'mensaje_cliente': a.mensaje_cliente,
                    'creado_en': a.creado_en.isoformat()} for a in c.avisos.all()],
        'mensajes': [{'id': m.id, 'autor': m.autor, 'texto': m.texto, 'creado_en': m.creado_en.isoformat(),
                      'pregunta': m.pregunta.pregunta if m.pregunta_id and m.pregunta else None}
                     for m in c.mensajes.filter(id__gt=despues).select_related('pregunta').order_by('id')],
    })


@api_view(['POST'])
def responder(request, pk):
    n = negocio_de(request.user)
    c = get_object_or_404(Conversacion, pk=pk, negocio=n)
    texto = (request.data.get('texto') or '').strip()
    if not 1 <= len(texto) <= 1000:
        return Response({'error': 'texto_invalido'}, status=400)
    with transaction.atomic():
        m = Mensaje.objects.create(conversacion=c, autor='dueno', texto=texto)
        Conversacion.objects.filter(pk=c.pk).update(estado='la_atiendes_tu', ultimo_mensaje_en=timezone.now())
    # F2-09: si el cliente escribió por WhatsApp, la respuesta le llega por WhatsApp.
    enviado = True
    if c.canal == 'whatsapp':
        from canales.whatsapp import enviar_texto
        enviado = enviar_texto(c, texto)
    return Response({'id': m.id, 'autor': m.autor, 'texto': m.texto, 'creado_en': m.creado_en.isoformat(),
                     'entregado': enviado}, status=201)


@api_view(['POST'])
def resolver(request, pk):
    n = negocio_de(request.user)
    c = get_object_or_404(Conversacion, pk=pk, negocio=n)
    with transaction.atomic():
        Aviso.objects.filter(conversacion=c, estado='pendiente').update(estado='resuelto', resuelto_en=timezone.now())
        Conversacion.objects.filter(pk=c.pk).update(estado='al_dia')
    from crm.servicios import registrar
    registrar(c, 'resuelta')
    return Response(status=204)


# --- Preguntas frecuentes -------------------------------------------------

def _pregunta_json(p):
    return {'id': str(p.id), 'tema': p.tema, 'pregunta': p.pregunta, 'otras_formas': p.otras_formas,
            'respuesta': p.respuesta, 'activa': p.activa, 'orden': p.orden}


def _validar_pregunta(d, parcial=False):
    limpio = {}
    if 'tema' in d or not parcial:
        if d.get('tema') not in dict(TEMAS):
            raise ValidationError('tema')
        limpio['tema'] = d['tema']
    if 'pregunta' in d or not parcial:
        t = (d.get('pregunta') or '').strip()
        if not 3 <= len(t) <= 150:
            raise ValidationError('pregunta')
        limpio['pregunta'] = t
    if 'respuesta' in d or not parcial:
        t = (d.get('respuesta') or '').strip()
        if not 1 <= len(t) <= 500:
            raise ValidationError('respuesta')
        limpio['respuesta'] = t
    if 'otras_formas' in d:
        t = (d.get('otras_formas') or '').strip()
        if len(t) > 300:
            raise ValidationError('otras_formas')
        limpio['otras_formas'] = t or None
    if 'activa' in d:
        limpio['activa'] = bool(d['activa'])
    return limpio


@api_view(['GET', 'POST'])
def preguntas(request):
    if request.method == 'GET':
        n = negocio_de(request.user)
        return Response([_pregunta_json(p) for p in n.preguntas.order_by('orden', 'pregunta')])
    n = negocio_de(request.user, solo_dueno=True)
    try:
        datos = _validar_pregunta(request.data)
    except ValidationError as e:
        return Response({'error': str(e.detail[0])}, status=400)
    orden = (n.preguntas.order_by('-orden').values_list('orden', flat=True).first() or 0) + 1
    try:
        with transaction.atomic():
            p = Pregunta.objects.create(negocio=n, orden=orden, **datos)
    except IntegrityError:
        return Response({'error': 'repetida'}, status=409)
    return Response(_pregunta_json(p), status=201)


@api_view(['PATCH', 'DELETE'])
def pregunta(request, pk):
    n = negocio_de(request.user, solo_dueno=True)
    p = get_object_or_404(Pregunta, pk=pk, negocio=n)
    if request.method == 'DELETE':
        p.delete()
        return Response(status=204)
    try:
        datos = _validar_pregunta(request.data, parcial=True)
    except ValidationError as e:
        return Response({'error': str(e.detail[0])}, status=400)
    for k, v in datos.items():
        setattr(p, k, v)
    try:
        with transaction.atomic():
            p.save()
    except IntegrityError:
        return Response({'error': 'repetida'}, status=409)
    return Response(_pregunta_json(p))


# --- Reportes -------------------------------------------------------------

@api_view(['GET'])
def reportes(request):
    """Los mismos números que la sección «Tu semana / Tu mes» del panel."""
    n = negocio_de(request.user)
    dias = 30 if request.GET.get('dias') == '30' else 7
    hoy = timezone.localdate()
    desde = timezone.make_aware(timezone.datetime.combine(hoy - timedelta(days=dias - 1), timezone.datetime.min.time()))
    convs = list(Conversacion.objects.filter(negocio=n, creada_en__gte=desde).values('id', 'creada_en'))
    avisos = list(Aviso.objects.filter(negocio=n, creado_en__gte=desde)
                  .values('conversacion_id', 'motivo', 'mensaje_cliente', 'creado_en'))
    respuestas = list(Mensaje.objects.filter(negocio=n, autor='asistente', pregunta__isnull=False, creado_en__gte=desde)
                      .values('pregunta__pregunta').annotate(veces=Count('id')).order_by('-veces')[:5])
    total_respuestas = Mensaje.objects.filter(negocio=n, autor='asistente', pregunta__isnull=False,
                                              creado_en__gte=desde).count()
    con_aviso = {a['conversacion_id'] for a in avisos}
    por_dia = {(hoy - timedelta(days=dias - 1 - i)).isoformat(): 0 for i in range(dias)}
    for c in convs:
        d = timezone.localtime(c['creada_en']).date().isoformat()
        if d in por_dia:
            por_dia[d] += 1
    return Response({
        'dias': dias,
        'conversaciones': len(convs),
        'te_necesitaron': sum(1 for c in convs if c['id'] in con_aviso),
        'respuestas': total_respuestas,
        'por_dia': [{'fecha': f, 'conversaciones': v} for f, v in por_dia.items()],
        'top': [{'pregunta': r['pregunta__pregunta'], 'veces': r['veces']} for r in respuestas],
        'no_sabe': [a['mensaje_cliente'] for a in sorted(avisos, key=lambda a: a['creado_en'], reverse=True)
                    if a['motivo'] == 'no_la_sabe'][:10],
        'motivos': {m: sum(1 for a in avisos if a['motivo'] == m)
                    for m in ('no_la_sabe', 'pidio_persona', 'pide_cita', 'queja_o_urgencia')},
    })
