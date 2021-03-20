from django.urls import path

from apps.avisos.views import ListarAvisosMaestroView, ListarAvisosAlumnoView, CrearAvisoView

urlpatterns = [
    path('<str:codigo_clase>/avisos', ListarAvisosMaestroView.as_view(), name='avisos'),
    path('<str:codigo_clase>/alumno/avisos', ListarAvisosAlumnoView.as_view(), name='avisos_alumno'),
    path('<str:codigo_clase>/crear_aviso', CrearAvisoView.as_view(), name='crear_aviso')
]
