"""Descarga en CSV de los envíos al CRM del negocio, para importarlos en Merkatics."""
import csv
import io

from django.http import HttpResponse

from negocios.permisos import con_negocio

COLUMNAS = ['nombre', 'telefono', 'organizacion', 'negocio', 'interes', 'resumen', 'atencion',
            'primer_mensaje', 'ultimo_mensaje', 'origen']


@con_negocio(solo_dueno=True)
def csv_crm(request):
    """Todos los envíos del negocio en un CSV que abre Excel."""
    n = request.negocio
    salida = io.StringIO()
    w = csv.writer(salida)
    w.writerow(['motivo', 'registrado', 'estado', *COLUMNAS])
    for e in n.envios_crm.order_by('-creado_en'):
        w.writerow([e.get_motivo_display(), e.creado_en.strftime('%d/%m/%Y %H:%M'), e.get_estado_display(),
                    *[e.datos.get(c, '') for c in COLUMNAS]])
    r = HttpResponse('﻿' + salida.getvalue(), content_type='text/csv; charset=utf-8')
    r['Content-Disposition'] = f'attachment; filename="crm-{n.slug}.csv"'
    return r
