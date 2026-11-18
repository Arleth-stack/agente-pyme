"""F2-11 · Envíos al CRM de Merkatics (ver docs/05_Integracion_Merkatics)."""
from django.db import models

from chat.models import Conversacion
from negocios.models import Negocio


class EnvioCRM(models.Model):
    MOTIVOS = [('cita', 'Pidió una cita'), ('resuelta', 'Conversación resuelta')]
    ESTADOS = [('pendiente', 'Pendiente'), ('enviado', 'Enviado'), ('fallo', 'Falló')]

    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE, related_name='envios_crm')
    conversacion = models.ForeignKey(Conversacion, on_delete=models.CASCADE, related_name='envios_crm')
    motivo = models.CharField(max_length=10, choices=MOTIVOS)
    # Exactamente los campos de la tabla 2 del documento de integración.
    datos = models.JSONField()
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')
    creado_en = models.DateTimeField(auto_now_add=True)
    enviado_en = models.DateTimeField(null=True, blank=True)
    respuesta = models.CharField(max_length=300, blank=True)

    class Meta:
        db_table = 'envios_crm'
        ordering = ['-creado_en']
        verbose_name = 'envío al CRM'
        verbose_name_plural = 'envíos al CRM'
