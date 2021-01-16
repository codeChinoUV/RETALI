from django.urls import path

from apps.avisos.views import consultar_avisos, crear_aviso

urlpatterns = [
    path('<str:codigo_clase>/avisos', consultar_avisos, name='avisos'),
    path('<str:codigo_clase>/crear_aviso', crear_aviso, name='crear_aviso')
]
