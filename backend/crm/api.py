"""F2-11 · Descarga en CSV de los envíos al CRM del negocio (para importarlos en Merkatics)."""
import csv
import io

from django.http import HttpResponse
from rest_framework.decorators import api_view

from negocios.servicios import negocio_de

COLUMNAS = ['nombre', 'telefono', 'organizacion', 'negocio', 'interes', 'resumen', 'atencion',
            'primer_mensaje', 'ultimo_mensaje', 'origen']


@api_view(['GET'])
def csv_crm(request):
    n = negocio_de(request.user, solo_dueno=True)
    salida = io.StringIO()
    w = csv.writer(salida)
    w.writerow(['motivo', 'registrado', 'estado', *COLUMNAS])
    for e in n.envios_crm.order_by('-creado_en'):
        w.writerow([e.get_motivo_display(), e.creado_en.strftime('%d/%m/%Y %H:%M'), e.get_estado_display(),
                    *[e.datos.get(c, '') for c in COLUMNAS]])
    r = HttpResponse('﻿' + salida.getvalue(), content_type='text/csv; charset=utf-8')
    r['Content-Disposition'] = f'attachment; filename="crm-{n.slug}.csv"'
    return r
