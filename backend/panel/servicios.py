"""Cálculos del panel que no son de una pantalla."""
from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from chat.models import Aviso, Conversacion, Mensaje


def reportes(n, dias=7):
    """Los números de «Tu semana» (7 días) o «Tu mes» (30 días)."""
    dias = 30 if dias == 30 else 7
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
    return {
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
    }

