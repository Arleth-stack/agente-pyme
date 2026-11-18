from django.contrib import admin

from .models import EnvioCRM


@admin.register(EnvioCRM)
class EnvioCRMAdmin(admin.ModelAdmin):
    list_display = ('negocio', 'motivo', 'estado', 'creado_en', 'enviado_en')
    list_filter = ('motivo', 'estado', 'negocio')
    readonly_fields = ('datos', 'respuesta')
