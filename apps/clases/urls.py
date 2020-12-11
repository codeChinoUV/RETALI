from django.urls import path, include

from apps.usuarios.views import pagina_inicio
from apps.clases.views import registrar_clase, informacion_clase, unirse_clase

urlpatterns = [
    path('', pagina_inicio, name='paginaInicio'),
    path('registro_clase/', registrar_clase, name='registrar_clase'),
    path('unirse_clase/', unirse_clase, name='unirse_clase'),
    path('<str:codigo_clase>/', informacion_clase, name='ver_materia'),
    path('', include('apps.actividades.urls'))
]
