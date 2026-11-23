"""Motor del chat: decide qué contestar a cada mensaje del cliente.

Es la traducción a Python de las funciones SQL de la Fase 1 (versión publicada
al 17 nov 2026: chat_decidir, buscar_pregunta, detectar_motivo, intencion,
sugerir, estado_horario…). La regla de oro no cambia: el chat solo contesta con
el texto que escribió el dueño o con datos del negocio (horario, dirección); si
no lo sabe, avisa a una persona. No inventa.
"""
import re
import unicodedata
from datetime import datetime, time
from zoneinfo import ZoneInfo

from django.db import transaction
from django.utils import timezone

# --- Texto ----------------------------------------------------------------

PALABRAS_RELLENO = frozenset("""
al algo alguien algun alguna ante aqui asi bien bueno buena buenas buenos buen
cada como con cual cuales cuando cuanto cuanta cuantos cuantas cuesta cuestan
costo costos cobran cobra precio precios sale salen del dia dias tardes noches
esta estan este esto eso esa ese estos esas esos hay hola las los les
mas muy mucho mucha muchas muchos para por pero que quisiera quiero queria
saber sea ser sin sus tus una unos unas uno usted ustedes favor gracias
oiga disculpe pregunta informacion info puedo pueden puede podria podrian
tienen tiene tengo hacen hace ofrecen manejan dan trabajan encuentran encuentra
queda quedan ahi alli nos sobre entre hasta desde tambien otra otro okey
hoy semana ahorita ahora luego todo todos toda todas
hacer hago sacar pedir ocupo gustaria tendran tendra manejas
tienes haces ofreces cobras vale valen cotizacion tarifa tarifas aproximadamente
servicio servicios mismo misma van son era seria fuera alguno algunos mio mia
""".split())

PALABRAS_GENERALES = frozenset("""
servicio servicios producto productos menu catalogo lista general opciones
ofrece venden vende dedican cosas tipo tipos informes ayuda manejan
cita pago donde horario telefono aceptan aceptar formas forma trabajos
clases clase actividades tratamientos tratamiento propiedades disponibles
paquetes planes platillos comida cursos reparaciones disciplinas
""".split())

PALABRAS_SALUDO = frozenset("""
hola buenas buenos buen dia dias tardes noches que tal saludos gracias
muchas mil ok okey va sale perfecto excelente adios bye hasta luego
gusto igualmente vale listo genial muy amable bien
""".split())

_SINONIMOS = {
    'donde': 'ubicado ubicados ubicada ubicacion direccion llego llegar mapa localizo',
    'cita': 'cita citas agendar agendo agende agenda reservar reservo reservacion reserva apartar aparto turno',
    'pago': 'pago pagos pagar tarjeta tarjetas efectivo transferencia transferencias deposito credito debito',
    'horario': ('horario horarios abren abre cierran cierra abierto abiertos abierta hora horas lunes martes '
                'miercoles jueves viernes sabado sabados domingo domingos festivos'),
    'telefono': 'telefono numero celular whatsapp contacto',
    'domicilio': 'domicilio envio envios entrega entregas reparto delivery llevan mandan',
    'auto': 'carro carros auto autos coche coches camioneta vehiculo vehiculos',
    'nino': 'nino ninos nina ninas hijo hijos hija hijas infantil bebe bebes chamacos',
    'cabello': 'cabello pelo',
    'diente': 'diente dientes muela muelas dental dentales',
    'caballero': 'hombre hombres caballero caballeros senor senores',
    'dama': 'mujer mujeres dama damas senora senoras',
}
SINONIMOS = {p: raiz for raiz, lista in _SINONIMOS.items() for p in lista.split()}

PRIORIDAD_TEMAS = ['precios', 'servicios', 'citas', 'horarios', 'ubicacion', 'pagos', 'otros']
PRIORIDAD_MOTIVO = {'queja_o_urgencia': 4, 'pide_cita': 3, 'pidio_persona': 2, 'no_la_sabe': 1}

DIAS_CLAVE = ['dom', 'lun', 'mar', 'mie', 'jue', 'vie', 'sab']
DIAS_NOMBRE = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado']


def normalizar(t):
    """Minúsculas, sin acentos, solo letras y números separados por un espacio."""
    t = unicodedata.normalize('NFD', t or '')
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn').lower()
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9]+', ' ', t)).strip()


def sinonimo(p):
    return SINONIMOS.get(p, p)


def palabras(t, ignorar=frozenset()):
    """Las palabras que importan de un texto (sin relleno ni el nombre del negocio)."""
    return {sinonimo(p) for p in normalizar(t).split(' ')
            if len(p) >= 3 and p not in PALABRAS_RELLENO and p not in ignorar}


def raiz(w):
    w = re.sub(r'(es|s)$', '', w, count=1)
    return re.sub(r'(ar|er|ir|an|en|as|os|a|e|o)$', '', w, count=1)


def _trigramas(w):
    # Igual que pg_trgm: dos espacios antes y uno después de cada palabra.
    s = f'  {w} '
    return {s[i:i + 3] for i in range(len(s) - 2)}


def similitud(a, b):
    ta, tb = _trigramas(a), _trigramas(b)
    return len(ta & tb) / len(ta | tb) if ta and tb else 0.0


def se_parecen(a, b):
    return a == b or (len(raiz(a)) >= 3 and raiz(a) == raiz(b)) or similitud(a, b) >= 0.5


_DIA_O_HORA = (r'(\b(lunes|martes|miercoles|jueves|viernes|sabado|domingo|hoy|manana|pasado manana)\b'
               r'|\ba las \d|\b\d{1,2}( ?(am|pm|hrs|horas))\b|\ben la (manana|tarde|noche)\b)')


def menciona_dia(texto):
    return re.search(_DIA_O_HORA, normalizar(texto)) is not None


def detectar_motivo(texto):
    n = normalizar(texto)
    if (re.search(r'\b(duele|dolor|sangra\w*|hinchad\w*|molest[ao]s?|enojad[ao]s?|queja\w*|reclam\w*|inconforme'
                  r'|pesimo|horrible|urgente)\b', n)
            or re.search(r'\b(cobraron de mas|dejaron mal|quedo mal|quedo peor|salio mal|hicieron mal|me lastimaron)\b', n)):
        return 'queja_o_urgencia'
    if (re.search(r'\b(hablar|comunicarme|comunicar|platicar|contactar|llamen|llamar|marquen)\b', n)
            or re.fullmatch(r'(con )?(una |un |el |la )?(persona|humano|alguien|asesor|asesora|encargado|encargada'
                            r'|duena|dueno)', n)):
        return 'pidio_persona'
    if (re.search(r'\b(cita\w*|agend\w*|apart\w*|reserv\w*|turno|espacio|lugar|llev\w*|ir|voy|pas\w*|ver|verme'
                  r'|atend\w*|atiend\w*)\b', n) and re.search(_DIA_O_HORA, n)):
        return 'pide_cita'
    return None


def intencion(texto):
    n = normalizar(texto)
    if re.search(r'\b(precio|precios|costo|costos|cuesta|cuestan|cobran|cobra|tarifas?|cotiza\w*)\b', n) \
            or re.search(r'\bcuanto (sale|es|vale)\b', n):
        return 'precios'
    if re.search(r'\b(citas?|agend\w*|reserv\w*|apart\w*|turno)\b', n):
        return 'citas'
    if re.search(r'\b(pagos?|pagar|tarjetas?|efectivo|transferencias?|deposito)\b', n):
        return 'pagos'
    if re.search(r'\b(donde|direccion|ubicacion|ubicados?|llego|llegar|mapa)\b', n):
        return 'ubicacion'
    if re.search(r'\b(horarios?|abren|cierran|hora)\b', n):
        return 'horarios'
    if re.search(r'\b(servicios?|ofrecen|ofrece|venden|vende|manejan|hacen|productos?|menu|catalogo|dedican)\b', n) \
            or re.search(r'\bque tienen\b', n):
        return 'servicios'
    if re.search(r'\b(informacion|info|informes|ayuda|opciones|ayudar)\b', n):
        return 'general'
    return None


def es_saludo(texto):
    n = normalizar(texto)
    return n != '' and set(n.split(' ')) <= PALABRAS_SALUDO


# --- Horario --------------------------------------------------------------

def _hora(hhmm):
    h, m = hhmm.split(':')
    return time(int(h), int(m))


def las(h):
    h12 = h.hour % 12 or 12
    return ('la ' if h12 == 1 else 'las ') + f'{h12}:{h.minute:02d}' + (' a. m.' if h < time(12) else ' p. m.')


def momento(negocio, hora=None):
    """La hora simulada (?hora=23:00) solo se acepta en los negocios de la demo."""
    return hora if hora is not None and negocio.es_demo else timezone.now()


def estado_horario(negocio, cuando):
    """→ (abierto, cierra, dia, abre). Igual que public.estado_horario."""
    local = cuando.astimezone(ZoneInfo(negocio.zona_horaria))
    ahora = local.time().replace(tzinfo=None)
    dow = (local.weekday() + 1) % 7  # 0 = domingo, como Postgres
    horario = negocio.horario or {}
    hoy = horario.get(DIAS_CLAVE[dow])
    if isinstance(hoy, dict):
        abre, cierra = _hora(hoy['abre']), _hora(hoy['cierra'])
        if abre <= ahora < cierra:
            return True, cierra, None, None
        if ahora < abre:
            return False, None, 'hoy', abre
    for i in range(1, 8):
        otro = horario.get(DIAS_CLAVE[(dow + i) % 7])
        if isinstance(otro, dict):
            dia = 'mañana' if i == 1 else 'el ' + DIAS_NOMBRE[(dow + i) % 7]
            return False, None, dia, _hora(otro['abre'])
    return False, None, None, None


def texto_cuando(abierto, dia, abre):
    if abierto or dia is None:
        return 'Te escriben en cuanto puedan.'
    return f'Ahorita estamos cerrados; te escriben {dia} a partir de {las(abre)}'


def texto_estado(abierto, cierra, dia, abre):
    if abierto:
        return f'Abierto · cierra a {las(cierra)}'
    if dia is None:
        return 'Cerrado'
    return f'Cerrado · abre {dia} a {las(abre)}'


# --- Preguntas del negocio ------------------------------------------------

def _activas(negocio):
    return list(negocio.preguntas.filter(activa=True).order_by('orden', 'pregunta'))


def temas_texto(negocio, preguntas=None):
    preguntas = _activas(negocio) if preguntas is None else preguntas
    temas = sorted({p.tema for p in preguntas if p.tema != 'otros'}, key=PRIORIDAD_TEMAS.index)
    g = negocio.giro
    etiquetas = {
        'precios': 'precios y mensualidades' if g == 'gimnasio' else 'precios',
        'servicios': {'consultorio': 'tratamientos', 'taller': 'reparaciones y servicios', 'gimnasio': 'clases',
                      'inmobiliaria': 'propiedades'}.get(g, 'servicios'),
        'citas': 'visitas' if g == 'inmobiliaria' else 'citas',
        'horarios': 'horario', 'ubicacion': 'cómo llegar', 'pagos': 'formas de pago',
    }
    a = [etiquetas[t] for t in temas]
    if not a:
        return 'lo que necesites'
    return a[0] if len(a) == 1 else ', '.join(a[:-1]) + ' y ' + a[-1]


def bienvenida(negocio, preguntas=None):
    frase = {
        'consultorio': 'Te ayudo a resolver tus dudas antes de tu consulta.',
        'salon': 'Te ayudo a preparar tu próxima visita.',
        'taller': 'Te ayudo con lo que necesite tu auto.',
        'gimnasio': 'Te ayudo a elegir tu clase o tu membresía.',
        'inmobiliaria': 'Te ayudo a encontrar la propiedad que buscas.',
    }.get(negocio.giro, 'Te ayudo con lo que necesites.')
    return (f'¡Hola! Gracias por escribir a {negocio.nombre}. {frase} Pregúntame por {temas_texto(negocio, preguntas)}. '
            'Si prefieres hablar con alguien del equipo, escribe «persona».')


def _formas(p):
    return [p.pregunta] + (p.otras_formas.split(',') if p.otras_formas else [])


def buscar_pregunta(negocio, texto, preguntas=None):
    """La pregunta frecuente que mejor explica el mensaje (≥ 60 % de sus palabras)."""
    preguntas = _activas(negocio) if preguntas is None else preguntas
    ignorar = palabras(negocio.nombre)
    m = palabras(texto, ignorar)
    if not m:
        return None
    mejor = None
    for p in preguntas:
        formas = [palabras(f, ignorar) for f in _formas(p)]
        vocab = set().union(*formas)
        if not vocab:
            continue
        cobertura = sum(1 for mw in m if any(se_parecen(mw, vw) for vw in vocab)) / len(m)
        if cobertura < 0.6:
            continue
        frases = [sum(1 for fw in f if any(se_parecen(mw, fw) for mw in m)) / len(f) for f in formas if f]
        frase = max(frases) if frases else None
        llave = (-cobertura, -(frase if frase is not None else -1), p.orden)
        if mejor is None or llave < mejor[0]:
            mejor = (llave, p)
    return mejor[1] if mejor else None


def sugerir(negocio, texto, cuantas=3, temas=None, preguntas=None):
    """Preguntas que el chat sí sabe contestar, para ofrecérselas al cliente."""
    preguntas = _activas(negocio) if preguntas is None else preguntas
    orden_temas = temas or PRIORIDAD_TEMAS
    m = palabras(texto) if texto is not None else set()
    candidatas, vistos_por_tema = [], {}
    for p in sorted(preguntas, key=lambda q: q.orden):
        if temas is not None and p.tema not in temas:
            continue
        vistos_por_tema[p.tema] = vistos_por_tema.get(p.tema, 0) + 1
        vocab = palabras(p.pregunta + ',' + (p.otras_formas or ''))
        comunes = sum(1 for mw in m for vw in vocab if se_parecen(mw, vw))
        prio = orden_temas.index(p.tema) + 1 if p.tema in orden_temas else 99
        candidatas.append((p, comunes, prio, vistos_por_tema[p.tema]))
    if texto is None:
        candidatas.sort(key=lambda c: (c[3] > 1, -c[1], c[2], c[0].orden))
    else:
        candidatas.sort(key=lambda c: (-c[1], c[2], c[0].orden))
    return [{'id': str(c[0].id), 'pregunta': c[0].pregunta} for c in candidatas[:cuantas]]


def lista_opciones(opciones):
    return '\n'.join(f'{i}. {o["pregunta"]}' for i, o in enumerate(opciones, 1))


# --- La decisión ----------------------------------------------------------

_DIVIDIR = re.compile(r'[?¿!.\n]+|\s+y\s+(?=(?:a qué|a que|cuánto|cuanto|dónde|donde|qué|que|tienen|hacen|aceptan'
                      r'|atienden|cómo|como)\b)')


def decidir(negocio, texto, cuando, conversacion=None):
    """→ dict(tipo, texto, pregunta, tema, motivo, abierto, opciones). Igual que public.chat_decidir."""
    from .models import Aviso, Mensaje

    preguntas = _activas(negocio)
    por_id = {str(p.id): p for p in preguntas}
    r = {'tipo': None, 'texto': None, 'pregunta': None, 'tema': None, 'motivo': None, 'abierto': None, 'opciones': None}
    norm = normalizar(texto)
    abierto, cierra, dia, abre = estado_horario(negocio, cuando)
    cuando_texto = texto_cuando(abierto, dia, abre)
    ignorar = palabras(negocio.nombre)
    mis_palabras = palabras(texto, ignorar)
    intento = intencion(texto)

    def faq(p):
        r.update(tipo='faq', texto=p.respuesta, pregunta=p, tema=p.tema)
        return r

    ya_habia, ultimas, ultimo = False, None, None
    if conversacion is not None:
        ya_habia = Aviso.objects.filter(conversacion=conversacion, estado='pendiente').exists()
        ultimo = (Mensaje.objects.filter(conversacion=conversacion, autor='asistente')
                  .select_related('pregunta').order_by('-id').first())
        ultimas = ultimo.opciones if ultimo else None

    # "2", "la 3", "opción 1": elige de la lista que se le acaba de ofrecer.
    if ultimas and re.fullmatch(r'(la |el |opcion |numero |la opcion |el numero )?\d{1,2}', norm):
        n = int(re.search(r'(\d{1,2})$', norm).group(1))
        if 1 <= n <= len(ultimas):
            p = por_id.get(str(ultimas[n - 1].get('id')))
            if p is not None:
                return faq(p)

    motivo = detectar_motivo(texto)
    # Si lo último que se habló fue de citas y el cliente da día u hora, es una cita.
    if motivo is None and conversacion is not None and menciona_dia(texto) and ultimo is not None and (
            (ultimo.pregunta is not None and ultimo.pregunta.tema == 'citas')
            or ultimo.texto.startswith('¡Claro! Dime qué día')):
        motivo = 'pide_cita'
    if motivo:
        inicio = {
            'queja_o_urgencia': 'Lamento mucho lo que pasó. Ya le avisé al equipo. ',
            'pidio_persona': 'Claro, ya le avisé a alguien del equipo para que te conteste. ',
            'pide_cita': '¡Con gusto! Ya le pasé tu solicitud al equipo para que te confirme el lugar. ',
        }[motivo]
        r.update(tipo='aviso', motivo=motivo, texto=inicio + cuando_texto)
        return r

    def texto_horario(prefijo):
        if abierto:
            return f'{prefijo}abiertos. Hoy cerramos a {las(cierra)}'
        if dia is None:
            return 'Ahorita estamos cerrados.'
        return f'Ahorita estamos cerrados. Abrimos {dia} a {las(abre)}'

    # "¿Están abiertos?", "¿a qué hora cierran hoy?"
    if re.search(r'\b(abiert[oa]s?|atendiendo|ya abrieron)\b', norm) or re.search(r'\b(abren|cierran|atienden) hoy\b', norm):
        r.update(tipo='horario', abierto=abierto, texto=texto_horario('Sí, ahorita estamos '))
        return r

    if es_saludo(texto):
        r['tipo'] = 'saludo'
        if re.search(r'(gracias|adios|bye|luego|gusto|amable)', norm):
            r['texto'] = '¡Con gusto! Aquí estoy si necesitas algo más.'
        else:
            opciones = sugerir(negocio, None, 4, preguntas=preguntas)
            r['texto'] = f'¡Hola! ¿En qué te puedo ayudar? Pregúntame por {temas_texto(negocio, preguntas)}.'
            if opciones:
                r['texto'] += '\n\nPor ejemplo:\n' + lista_opciones(opciones)
                r['opciones'] = opciones
        return r

    # 1. La pregunta frecuente que mejor explica el mensaje completo.
    p = buscar_pregunta(negocio, texto, preguntas)
    if p is not None:
        return faq(p)

    # 2. Varias preguntas en un mensaje: "¿cuánto cuesta la limpieza? ¿y a qué hora abren?"
    partes = [x for x in _DIVIDIR.split(texto) if x != '']
    if len(partes) >= 2:
        encontradas, sin_respuesta = [], False
        for parte in partes:
            q = buscar_pregunta(negocio, parte, preguntas)
            if q is not None:
                if q not in encontradas:
                    encontradas.append(q)
            elif palabras(parte, ignorar) and not es_saludo(parte):
                sin_respuesta = True
        if encontradas:
            r.update(texto='\n\n'.join(q.respuesta for q in encontradas), tema=encontradas[0].tema,
                     pregunta=encontradas[0])
            if sin_respuesta:
                r.update(tipo='aviso', motivo='no_la_sabe',
                         texto=r['texto'] + '\n\nLo demás se lo pasé al equipo. ' + cuando_texto)
            else:
                r['tipo'] = 'varias' if len(encontradas) > 1 else 'faq'
            return r

    # 3. Pregunta general de un tema: "¿qué precios tienen?", "¿qué ofrecen?", "quiero una cita".
    if mis_palabras <= PALABRAS_GENERALES:
        if intento in ('precios', 'servicios'):
            def general(q):
                return palabras(q.pregunta, ignorar) <= PALABRAS_GENERALES
            cand = [q for q in preguntas if q.tema == intento and (
                general(q) or (intento == 'servicios' and re.match(r'(que|cuales)\b', normalizar(q.pregunta))))]
            cand.sort(key=lambda q: (not general(q), q.orden))
            if cand:
                return faq(cand[0])

        if intento == 'precios':
            de_precios = [q for q in preguntas if q.tema == 'precios']
            if len(de_precios) == 1:
                return faq(de_precios[0])
            if len(de_precios) > 1:
                lista = sorted(de_precios, key=lambda q: q.orden)[:8]
                r.update(tipo='temas', tema='precios',
                         texto='Estos son nuestros precios:\n' + '\n'.join('• ' + q.respuesta for q in lista))
                return r
        elif intento in ('citas', 'pagos', 'ubicacion', 'horarios'):
            del_tema = sorted((q for q in preguntas if q.tema == intento), key=lambda q: q.orden)
            if del_tema:
                return faq(del_tema[0])
            if intento == 'citas':
                r.update(tipo='pide_dia', tema='citas',
                         texto='¡Claro! Dime qué día y a qué hora te gustaría, y se lo paso al equipo para que te confirme.')
                return r
            # Sin pregunta escrita, el horario y la dirección salen de los datos del negocio.
            if intento == 'horarios':
                r.update(tipo='horario', abierto=abierto, tema='horarios', texto=texto_horario('Ahorita estamos '))
                return r
            if intento == 'ubicacion' and (negocio.direccion or '').strip():
                r.update(tipo='faq', tema='ubicacion',
                         texto='Estamos en ' + re.sub(r'\.$', '', negocio.direccion.strip()) + '.')
                return r

        # Menú: lo que sí sabe contestar, para que el cliente elija.
        if intento in (None, 'servicios', 'general'):
            opciones = sugerir(negocio, None, 6, ['servicios', 'precios', 'otros'] if intento == 'servicios' else None,
                               preguntas=preguntas)
            if not opciones:
                opciones = sugerir(negocio, None, 6, preguntas=preguntas)
            if opciones:
                r.update(tipo='menu', tema='servicios' if intento == 'servicios' else None, opciones=opciones,
                         texto=f'En {negocio.nombre} te puedo contar de esto:\n' + lista_opciones(opciones)
                         + '\n\nEscríbeme el número o tu pregunta.')
                return r

    # 4. No la sabe: avisa al equipo y, mientras, ofrece lo que sí sabe.
    r.update(tipo='aviso', motivo='no_la_sabe', texto=(
        'Esa también se la pasé al equipo. ' if ya_habia
        else 'Esa no la tengo a la mano, pero ya le pasé tu pregunta al equipo. ') + cuando_texto)
    opciones = sugerir(negocio, texto, 3, preguntas=preguntas)
    if opciones:
        r['texto'] += '\n\nMientras, te puedo ayudar con esto:\n' + lista_opciones(opciones)
        r['opciones'] = opciones
    return r


INTERES_POR_MOTIVO = {'queja_o_urgencia': 'queja', 'pide_cita': 'cita'}
INTERES_POR_TEMA = {'precios': 'precio', 'citas': 'cita', 'servicios': 'servicio', 'ubicacion': 'ubicacion'}


def recibir(conversacion, texto, hora=None, redactar=None):
    """El cliente escribió: guarda su mensaje, decide, avisa si hace falta y contesta.

    `redactar(negocio, texto_cliente, decision)` (F2-08) puede devolver un texto
    más natural; si devuelve None o falla, se usa el texto exacto.
    Regresa (mensaje_cliente, mensaje_respuesta, decision).
    """
    from .models import Aviso, Conversacion, Mensaje

    texto = (texto or '').strip()
    if not 1 <= len(texto) <= 1000:
        raise ValueError('texto_invalido')

    with transaction.atomic():
        # Candado por conversación: dos mensajes al mismo tiempo no crean dos avisos.
        conv = Conversacion.objects.select_for_update().select_related('negocio').get(pk=conversacion.pk)
        negocio = conv.negocio
        d = decidir(negocio, texto, momento(negocio, hora), conv)

        ahora = timezone.now()
        cliente = Mensaje.objects.create(conversacion=conv, autor='cliente', texto=texto)

        if d['tipo'] == 'aviso':
            pendiente = Aviso.objects.filter(conversacion=conv, estado='pendiente').first()
            if pendiente is None:
                Aviso.objects.create(conversacion=conv, motivo=d['motivo'], mensaje_cliente=texto)
            elif PRIORIDAD_MOTIVO[d['motivo']] > PRIORIDAD_MOTIVO[pendiente.motivo]:
                pendiente.motivo, pendiente.mensaje_cliente = d['motivo'], texto
                pendiente.save(update_fields=['motivo', 'mensaje_cliente'])

        final, original = d['texto'], None
        if redactar is not None:
            try:
                otro = redactar(negocio, texto, d)
            except Exception:  # noqa: BLE001 — si la redacción falla, se usa el texto exacto
                otro = None
            if otro and otro.strip() and otro.strip() != d['texto']:
                final, original = otro.strip()[:1000], d['texto']

        respuesta = Mensaje.objects.create(conversacion=conv, autor='asistente', texto=final,
                                           texto_original=original, pregunta=d['pregunta'], opciones=d['opciones'])

        conv.ultimo_mensaje_en = ahora
        conv.ultimo_mensaje_cliente_en = ahora
        if d['tipo'] == 'aviso':
            conv.estado = 'te_necesita'
        if d['motivo'] in INTERES_POR_MOTIVO:
            conv.interes = INTERES_POR_MOTIVO[d['motivo']]
        elif d['tema'] is not None:
            conv.interes = INTERES_POR_TEMA.get(d['tema'], 'otro')
        conv.save(update_fields=['ultimo_mensaje_en', 'ultimo_mensaje_cliente_en', 'estado', 'interes'])
    return cliente, respuesta, d


def estado_publico(negocio, hora=None):
    """Lo que el chat muestra arriba: nombre, abierto/cerrado, bienvenida y sugerencias."""
    preguntas = _activas(negocio)
    abierto, cierra, dia, abre = estado_horario(negocio, momento(negocio, hora))
    return {
        'nombre': negocio.nombre,
        'giro': negocio.giro,
        'abierto': abierto,
        'estado': texto_estado(abierto, cierra, dia, abre),
        'bienvenida': bienvenida(negocio, preguntas),
        'sugerencias': [o['pregunta'] for o in sugerir(negocio, None, 4, preguntas=preguntas)],
    }
