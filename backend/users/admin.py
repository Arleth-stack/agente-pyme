from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Cuentas que entran con su WhatsApp."""

    ordering = ('-date_joined',)
    list_display = ('telefono', 'nombre', 'correo', 'is_staff', 'date_joined')
    search_fields = ('telefono', 'nombre', 'correo')
    fieldsets = (
        (None, {'fields': ('telefono', 'password')}),
        ('Datos', {'fields': ('nombre', 'correo')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = ((None, {'classes': ('wide',), 'fields': ('telefono', 'password1', 'password2')}),)
