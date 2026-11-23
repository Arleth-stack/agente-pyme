from django.urls import path

from . import views

app_name = 'pagos'

urlpatterns = [
    path('prueba/', views.prueba, name='prueba'),
    path('portal/', views.portal, name='portal'),
    path('aviso-stripe/', views.aviso_stripe, name='aviso_stripe'),
]
