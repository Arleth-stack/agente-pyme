"""Conversaciones del chat, sus mensajes y los avisos al dueño."""
import uuid

from django.db import models
from django.db.models import Q

from negocios.models import Negocio, Pregunta

ESTADOS = [('al_dia', 'Al día'), ('te_necesita', 'Te necesita'), ('la_atiendes_tu', 'La atiendes tú')]
INTERESES = [('precio', 'Precio'), ('cita', 'Cita'), ('servicio', 'Servicio'),
             ('ubicacion', 'Ubicación'), ('queja', 'Queja'), ('otro', 'Otro')]
AUTORES = [('cliente', 'Cliente'), ('asistente', 'Asistente'), ('dueno', 'Dueño')]
MOTIVOS = [('no_la_sabe', 'No la sabe'), ('pidio_persona', 'Pidió una persona'),
           ('pide_cita', 'Pide una cita'), ('queja_o_urgencia', 'Queja o urgencia')]
CANALES = [('web', 'Chat web'), ('whatsapp', 'WhatsApp')]


class Conversacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE, related_name='conversaciones')
    # El cliente del chat web solo conoce su token; con él lee y escribe su conversación.
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    canal = models.CharField(max_length=10, choices=CANALES, default='web')
    # En WhatsApp, el número del cliente con lada internacional (p. ej. 5215512345678).
    whatsapp_cliente = models.CharField(max_length=20, null=True, blank=True)
    cliente_nombre = models.CharField(max_length=60, null=True, blank=True)
    cliente_telefono = models.CharField(max_length=10, null=True, blank=True)
    estado = models.CharField(max_length=16, choices=ESTADOS, default='al_dia')
    interes = models.CharField(max_length=10, choices=INTERESES, null=True, blank=True)
    resumen = models.CharField(max_length=200, null=True, blank=True)
    creada_en = models.DateTimeField(auto_now_add=True)
    ultimo_mensaje_en = models.DateTimeField(auto_now_add=True)
    ultimo_mensaje_cliente_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'conversaciones'
        ordering = ['-ultimo_mensaje_en']
        indexes = [
            models.Index(fields=['negocio', '-ultimo_mensaje_en'], name='conv_por_negocio'),
            models.Index(fields=['negocio', 'whatsapp_cliente'], name='conv_por_whatsapp'),
        ]
        constraints = [
            models.CheckConstraint(condition=Q(estado__in=[e for e, _ in ESTADOS]), name='conv_estado_valido'),
            models.CheckConstraint(condition=Q(interes__isnull=True) | Q(interes__in=[i for i, _ in INTERESES]),
                                   name='conv_interes_valido'),
            models.CheckConstraint(condition=Q(cliente_telefono__isnull=True) | Q(cliente_telefono__regex=r'^[0-9]{10}$'),
                                   name='conv_telefono_10'),
        ]


class Mensaje(models.Model):
    id = models.BigAutoField(primary_key=True)
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE, related_name='mensajes')
    conversacion = models.ForeignKey(Conversacion, on_delete=models.CASCADE, related_name='mensajes')
    autor = models.CharField(max_length=10, choices=AUTORES)
    texto = models.TextField(max_length=1000)
    pregunta = models.ForeignKey(Pregunta, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    # Lista que se le ofreció al cliente: [{"id": "...", "pregunta": "..."}]
    opciones = models.JSONField(null=True, blank=True)
    # F2-08: si la respuesta la redactó Gemini, aquí queda el texto exacto del dueño.
    texto_original = models.TextField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mensajes'
        ordering = ['id']
        indexes = [models.Index(fields=['conversacion', 'id'], name='msj_por_conversacion')]
        constraints = [
            models.CheckConstraint(condition=Q(autor__in=[a for a, _ in AUTORES]), name='msj_autor_valido'),
        ]

    def save(self, *args, **kwargs):
        # El negocio del mensaje siempre es el de su conversación (como el disparador de la Fase 1).
        self.negocio_id = self.conversacion.negocio_id
        super().save(*args, **kwargs)


class Aviso(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE, related_name='avisos')
    conversacion = models.ForeignKey(Conversacion, on_delete=models.CASCADE, related_name='avisos')
    motivo = models.CharField(max_length=20, choices=MOTIVOS)
    mensaje_cliente = models.TextField()
    estado = models.CharField(max_length=10, default='pendiente',
                              choices=[('pendiente', 'Pendiente'), ('resuelto', 'Resuelto')])
    creado_en = models.DateTimeField(auto_now_add=True)
    resuelto_en = models.DateTimeField(null=True, blank=True)
    # F2-10: cuándo se le avisó al dueño fuera del panel.
    notificado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'avisos'
        ordering = ['-creado_en']
        constraints = [
            models.CheckConstraint(condition=Q(motivo__in=[m for m, _ in MOTIVOS]), name='aviso_motivo_valido'),
            models.CheckConstraint(condition=Q(estado__in=['pendiente', 'resuelto']), name='aviso_estado_valido'),
        ]
        # «Un solo aviso pendiente por conversación» lo cuida el motor con un candado
        # (MySQL no tiene índices únicos con condición).

    def save(self, *args, **kwargs):
        self.negocio_id = self.conversacion.negocio_id
        super().save(*args, **kwargs)
