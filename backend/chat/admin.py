from django.contrib import admin

from .models import Aviso, Conversacion, Mensaje


class MensajeEnLinea(admin.TabularInline):
    model = Mensaje
    extra = 0
    fields = ('autor', 'texto', 'texto_original', 'creado_en')
    readonly_fields = fields


@admin.register(Conversacion)
class ConversacionAdmin(admin.ModelAdmin):
    list_display = ('negocio', 'canal', 'cliente_nombre', 'estado', 'interes', 'ultimo_mensaje_en')
    list_filter = ('canal', 'estado', 'negocio')
    inlines = [MensajeEnLinea]


@admin.register(Aviso)
class AvisoAdmin(admin.ModelAdmin):
    list_display = ('negocio', 'motivo', 'estado', 'creado_en', 'notificado_en')
    list_filter = ('motivo', 'estado', 'negocio')
