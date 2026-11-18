from django.contrib import admin

from .models import CanalWhatsApp


@admin.register(CanalWhatsApp)
class CanalWhatsAppAdmin(admin.ModelAdmin):
    list_display = ('negocio', 'numero_visible', 'phone_number_id', 'activo')
