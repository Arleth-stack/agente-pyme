from django.urls import path

from . import views

app_name = 'negocios'

urlpatterns = [
    path('', views.crear, name='crear'),
]
