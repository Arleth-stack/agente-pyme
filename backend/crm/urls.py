from django.urls import path

from . import views

app_name = 'crm'

urlpatterns = [
    path('envios.csv', views.csv_crm, name='csv'),
]
