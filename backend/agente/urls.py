"""Direcciones del backend de la Fase 2.

/api/chat/…      chat público (cliente del negocio, sin cuenta)
/api/cuentas/…   registro, entrar, salir, yo
/api/negocios/…  alta del negocio
/api/panel/…     panel del dueño (con su token)
/api/whatsapp/webhook  WhatsApp real (Meta)
/admin/          administración de Merkatics
"""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path

from canales.whatsapp import webhook
from chat import api as chat
from crm.api import csv_crm
from negocios import api as neg
from negocios import pagos

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/salud', lambda r: JsonResponse({'ok': True})),

    path('api/chat/<slug:slug>', chat.negocio),
    path('api/chat/<slug:slug>/iniciar', chat.iniciar),
    path('api/chat-enviar', chat.enviar),
    path('api/chat-mensajes', chat.mensajes),
    path('api/demo/negocios', chat.negocios_demo),

    path('api/cuentas/registro', neg.registro),
    path('api/cuentas/entrar', neg.entrar),
    path('api/cuentas/salir', neg.salir),
    path('api/cuentas/yo', neg.yo),
    path('api/negocios/crear', neg.crear),

    path('api/panel/negocio', neg.mi_negocio),
    path('api/panel/conversaciones', neg.conversaciones),
    path('api/panel/conversaciones/<uuid:pk>', neg.conversacion),
    path('api/panel/conversaciones/<uuid:pk>/responder', neg.responder),
    path('api/panel/conversaciones/<uuid:pk>/resolver', neg.resolver),
    path('api/panel/preguntas', neg.preguntas),
    path('api/panel/preguntas/<uuid:pk>', neg.pregunta),
    path('api/panel/reportes', neg.reportes),
    path('api/panel/crm.csv', csv_crm),

    path('api/panel/plan', pagos.plan),
    path('api/panel/plan/prueba', pagos.prueba),
    path('api/panel/plan/portal', pagos.portal),
    path('api/stripe-aviso', pagos.aviso_stripe),

    path('api/whatsapp/webhook', webhook),
]
