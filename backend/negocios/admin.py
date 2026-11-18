from django.contrib import admin

from .models import Miembro, Negocio, Pregunta


class PreguntaEnLinea(admin.TabularInline):
    model = Pregunta
    extra = 0
    fields = ('orden', 'tema', 'pregunta', 'respuesta', 'activa')


class MiembroEnLinea(admin.TabularInline):
    model = Miembro
    extra = 0
    raw_id_fields = ('usuario',)


@admin.register(Negocio)
class NegocioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'giro', 'plan_estado', 'es_demo', 'creado_en')
    list_filter = ('giro', 'plan_estado', 'es_demo')
    search_fields = ('nombre', 'slug')
    readonly_fields = ('creado_en', 'plan_actualizado', 'stripe_cliente', 'stripe_suscripcion')
    inlines = [MiembroEnLinea, PreguntaEnLinea]
