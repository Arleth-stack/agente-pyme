from django.urls import path

from . import views

app_name = 'chat'

urlpatterns = [
    path('enviar/', views.enviar, name='enviar'),
    path('mensajes/', views.mensajes, name='mensajes'),
    path('<slug:slug>/', views.pantalla, name='pantalla'),
    path('<slug:slug>/estado/', views.estado, name='estado'),
    path('<slug:slug>/iniciar/', views.iniciar, name='iniciar'),
]
