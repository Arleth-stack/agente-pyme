"""Qué número de WhatsApp (Meta) es de qué negocio."""
from django.db import models

from negocios.models import Negocio


class CanalWhatsApp(models.Model):
    negocio = models.OneToOneField(Negocio, on_delete=models.CASCADE, related_name='whatsapp')
    # «Phone number ID» que Meta da en WhatsApp → Configuración de la API.
    phone_number_id = models.CharField(max_length=40, unique=True)
    numero_visible = models.CharField(max_length=20, blank=True, help_text='Ej. +52 55 1234 5678')
    # Solo si los avisos deben ir a otro número que el de la cuenta del dueño (con lada, p. ej. 525512345678).
    dueno_whatsapp = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'canales_whatsapp'
        verbose_name = 'canal de WhatsApp'
        verbose_name_plural = 'canales de WhatsApp'

    def __str__(self):
        return f'{self.negocio} · {self.numero_visible or self.phone_number_id}'


class RecibidoWhatsApp(models.Model):
    """Meta a veces manda el mismo mensaje dos veces: así se contesta una sola."""
    wamid = models.CharField(max_length=200, unique=True)
    recibido_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'whatsapp_recibidos'
