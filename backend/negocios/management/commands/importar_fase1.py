"""F2-05 · Mudanza de los datos de la Fase 1 (Supabase) a MySQL.

    python manage.py importar_fase1 /ruta/fase1.json

El archivo lo genera el script de exportación (tablas públicas + cuentas de
dueños con su contraseña en bcrypt). Conserva los mismos identificadores, así
los enlaces y tokens de la Fase 1 siguen sirviendo. Se puede correr varias
veces: lo que ya existe se actualiza, no se duplica.
"""
import json
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from chat.models import Aviso, Conversacion, Mensaje
from negocios.models import Miembro, Negocio, Pregunta


def fecha(v):
    return datetime.fromisoformat(v.replace('Z', '+00:00')) if v else None


class Command(BaseCommand):
    help = 'Importa a MySQL los datos exportados de Supabase (Fase 1).'

    def add_arguments(self, parser):
        parser.add_argument('archivo')

    @transaction.atomic
    def handle(self, archivo, **opciones):
        with open(archivo, encoding='utf-8') as f:
            d = json.load(f)
        User = get_user_model()

        usuarios = {}
        for u in d['usuarios']:
            correo = u['email'].strip().lower()
            usuario, _ = User.objects.update_or_create(
                username=correo[:150],
                defaults={'email': correo, 'date_joined': fecha(u['created_at']),
                          'last_login': fecha(u.get('last_sign_in_at')),
                          # Supabase guarda bcrypt ($2a$…); Django lo reconoce con el prefijo «bcrypt$».
                          'password': 'bcrypt$' + u['encrypted_password']})
            usuarios[u['id']] = usuario

        campos_negocio = ['slug', 'nombre', 'giro', 'telefono', 'direccion', 'zona_horaria', 'horario', 'es_demo',
                          'merkatics_org_id', 'plan_estado', 'stripe_cliente', 'stripe_suscripcion']
        for n in d['negocios']:
            Negocio.objects.update_or_create(id=n['id'], defaults={
                **{c: n[c] for c in campos_negocio},
                'prueba_termina': fecha(n['prueba_termina']), 'plan_termina': fecha(n['plan_termina']),
                'plan_actualizado': fecha(n['plan_actualizado'])})
            Negocio.objects.filter(id=n['id']).update(creado_en=fecha(n['creado_en']))

        for m in d['miembros']:
            Miembro.objects.update_or_create(negocio_id=m['negocio_id'], usuario=usuarios[m['usuario_id']],
                                             defaults={'rol': m['rol']})

        for p in d['preguntas']:
            Pregunta.objects.update_or_create(id=p['id'], defaults={
                'negocio_id': p['negocio_id'], 'tema': p['tema'], 'pregunta': p['pregunta'],
                'otras_formas': p['otras_formas'], 'respuesta': p['respuesta'], 'activa': p['activa'],
                'orden': p['orden']})

        for c in d['conversaciones']:
            Conversacion.objects.update_or_create(id=c['id'], defaults={
                'negocio_id': c['negocio_id'], 'token': c['token'], 'cliente_nombre': c['cliente_nombre'],
                'cliente_telefono': c['cliente_telefono'], 'estado': c['estado'], 'interes': c['interes'],
                'resumen': c['resumen']})
            Conversacion.objects.filter(id=c['id']).update(creada_en=fecha(c['creada_en']),
                                                           ultimo_mensaje_en=fecha(c['ultimo_mensaje_en']))

        for m in sorted(d['mensajes'], key=lambda x: x['id']):
            conv = Conversacion.objects.get(id=m['conversacion_id'])
            obj, _ = Mensaje.objects.update_or_create(id=m['id'], defaults={
                'conversacion': conv, 'autor': m['autor'], 'texto': m['texto'],
                'pregunta_id': m['pregunta_id'] if Pregunta.objects.filter(id=m['pregunta_id']).exists() else None,
                'opciones': m['opciones']})
            Mensaje.objects.filter(id=obj.id).update(creado_en=fecha(m['creado_en']))

        for a in d['avisos']:
            conv = Conversacion.objects.get(id=a['conversacion_id'])
            Aviso.objects.update_or_create(id=a['id'], defaults={
                'conversacion': conv, 'motivo': a['motivo'], 'mensaje_cliente': a['mensaje_cliente'],
                'estado': a['estado'], 'resuelto_en': fecha(a['resuelto_en'])})
            Aviso.objects.filter(id=a['id']).update(creado_en=fecha(a['creado_en']))

        # Que los mensajes nuevos sigan numerándose después de los importados.
        from django.db import connection
        ultimo = max((m['id'] for m in d['mensajes']), default=0)
        with connection.cursor() as cur:
            cur.execute(f'ALTER TABLE mensajes AUTO_INCREMENT = {int(ultimo) + 1}')

        self.stdout.write(self.style.SUCCESS(
            f"Importado: {len(d['negocios'])} negocios, {len(usuarios)} cuentas, {len(d['preguntas'])} preguntas, "
            f"{len(d['conversaciones'])} conversaciones, {len(d['mensajes'])} mensajes, {len(d['avisos'])} avisos."))
