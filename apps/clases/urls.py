from django.urls import path, include

from apps.usuarios.views import pagina_inicio
from apps.clases.views import registrar_clase, informacion_clase, obtener_informacion_clase, unir_alumno_a_clase, \
    informacion_clase_alumno

urlpatterns = [
    path('', pagina_inicio, name='paginaInicio'),
    path('registro_clase/', registrar_clase, name='registrar_clase'),
    path('obtener_informacion_clase/<str:codigo_clase>', obtener_informacion_clase, name='obtener_informacion_clase'),
    path('<str:codigo_clase>/', informacion_clase, name='ver_materia'),
    path('<str:codigo_clase>/_alumno', informacion_clase_alumno, name='ver_materia_alumno'),
    path('unirse_a_clase/<str:codigo_clase>', unir_alumno_a_clase, name='unirse_a_clase'),
    path('', include('apps.actividades.urls')),
    path('', include('apps.foros.urls')),
    path('', include('apps.avisos.urls'))
]
