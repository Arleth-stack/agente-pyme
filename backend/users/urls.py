from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('entrar/', views.entrar, name='entrar'),
    path('salir/', views.salir, name='salir'),
]
