"""Direcciones del sitio: junta las de cada app."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('inicio.urls')),
    path('cuenta/', include('users.urls')),
    path('crear/', include('negocios.urls')),
    path('chat/', include('chat.urls')),
    path('panel/', include('panel.urls')),
    path('pagos/', include('pagos.urls')),
    path('whatsapp/', include('canales.urls')),
    path('crm/', include('crm.urls')),
    path('admin/', admin.site.urls),
]
