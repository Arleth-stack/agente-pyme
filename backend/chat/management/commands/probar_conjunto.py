"""F2-03 · Corre el conjunto de prueba P1 (pruebas/conjunto.json) contra el motor en Python.

    python manage.py probar_conjunto

Hace lo mismo que pruebas/correr.mjs de la Fase 1: un cliente nuevo por caso,
manda el mensaje y revisa la respuesta. Todo pasa dentro de una transacción que
se deshace al final, así que no deja conversaciones en los paneles.
Guarda el resultado en pruebas/resultados/<fecha>_P1_python.md.
"""
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from chat.models import Conversacion
from chat.motor import recibir
from negocios.models import Negocio, Pregunta

RAIZ = Path(__file__).resolve().parents[4]
NOMBRES = {'consultorio-dental-sonrisa-clara': 'Sonrisa Clara', 'salon-bella': 'Salón Bella',
           'taller-rapido': 'Taller Rápido'}


class Command(BaseCommand):
    help = 'Corre el conjunto de prueba P1 contra el motor del chat en Python.'

    def add_arguments(self, parser):
        parser.add_argument('--hora', help='Hora simulada para los casos sin hora (ISO, p. ej. 2026-11-18T12:00-06:00)')

    def handle(self, **opciones):
        hora_fija = datetime.fromisoformat(opciones['hora']) if opciones.get('hora') else None
        conjunto = json.loads((RAIZ / 'pruebas' / 'conjunto.json').read_text(encoding='utf-8'))
        respuestas = {f'{p.negocio.slug}|{p.pregunta}': p.respuesta
                      for p in Pregunta.objects.select_related('negocio')}
        resultados = []

        with transaction.atomic():
            for slug, casos in conjunto.items():
                if slug.startswith('_'):
                    continue
                negocio = Negocio.objects.get(slug=slug)
                for caso in casos:
                    conv = Conversacion.objects.create(negocio=negocio)
                    hora = (datetime.fromisoformat(caso['hora'].replace('Z', '+00:00')) if caso.get('hora')
                            else hora_fija)
                    _, r, d = recibir(conv, caso['texto'], hora=hora)
                    e = caso['espera']
                    if 'respuesta_de' in e:
                        esperado = respuestas.get(f"{slug}|{e['respuesta_de']}")
                        ok = r.texto == esperado
                    elif 'aviso' in e:
                        esperado, ok = f"aviso {e['aviso']}", d['motivo'] == e['aviso']
                    elif 'saludo' in e:
                        esperado, ok = 'saludo sin aviso', d['tipo'] == 'saludo'
                    else:
                        esperado = 'abierto' if e['abierto'] else 'cerrado'
                        ok = d['tipo'] == 'horario' and d['abierto'] == e['abierto']
                    obtuvo = ' '.join(x for x in (d['tipo'], d['motivo'] or '', r.texto) if x)
                    resultados.append({**caso, 'slug': slug, 'ok': ok, 'esperado': esperado, 'obtuvo': obtuvo})
            transaction.set_rollback(True)

        por_tipo = defaultdict(lambda: [0, 0])
        for r in resultados:
            por_tipo[r['tipo']][1] += 1
            por_tipo[r['tipo']][0] += r['ok']
        fallas = [r for r in resultados if not r['ok']]
        cubiertas = [r for r in resultados if r['tipo'] in ('faq', 'otra_forma')]
        pct = round(100 * sum(r['ok'] for r in cubiertas) / len(cubiertas)) if cubiertas else 100
        inventadas = sum(1 for r in resultados if 'aviso' in r['espera'] and r['obtuvo'].startswith('faq'))
        ahora = timezone.localtime().strftime('%d/%m/%Y %H:%M')

        celda = lambda t: ' '.join(str(t or '').replace('|', '/').split())[:110]  # noqa: E731
        lineas = [
            f'# Resultado P1 con el motor en Python (Fase 2) — {ahora}', '',
            f'Total: {len(resultados) - len(fallas)} de {len(resultados)} · Cubiertas correctas: {pct} % (meta ≥ 90 %)'
            f' · Inventadas: {inventadas} (meta 0)', '',
            '| Tipo | Aprobadas |', '|---|---|',
            *[f'| {t} | {v[0]} de {v[1]} |' for t, v in por_tipo.items()], '',
            '## Fallas' if fallas else '## Sin fallas',
            *[f"- **{f['slug']}** · {f['tipo']} · «{f['texto']}» → esperaba {str(f['esperado'])[:60]}… · obtuvo: {f['obtuvo'][:90]}"
              for f in fallas],
            '', '## Los casos uno por uno', '',
            '| Negocio | Tipo | El cliente escribe | Se esperaba | El chat contestó | Bien |', '|---|---|---|---|---|---|',
            *[f"| {NOMBRES.get(r['slug'], r['slug'])} | {r['tipo']} | {celda(r['texto'])} | {celda(r['esperado'])} | "
              f"{celda(r['obtuvo'])} | {'sí' if r['ok'] else '**no**'} |" for r in resultados],
        ]
        salida = RAIZ / 'pruebas' / 'resultados' / f"{timezone.localdate().isoformat()}_P1_python.md"
        salida.write_text('\n'.join(lineas) + '\n', encoding='utf-8')
        self.stdout.write('\n'.join(lineas[:12 + len(por_tipo) + len(fallas)]))
        self.stdout.write(f'\nGuardado en {salida.relative_to(RAIZ)}')
