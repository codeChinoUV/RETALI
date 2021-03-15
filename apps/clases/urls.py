from django.urls import path, include

from apps.usuarios.views import InicioView
from apps.clases.views import obtener_informacion_clase, ListarAlumnosDeClase, ModificarEstadoInscriocionAlumno, \
    RegistroClaseView, ConsultarClaseView, SolicitarUnirseAClaseView, ConsultarClaseAlumnoView

urlpatterns = [
    path('', InicioView.as_view(), name='inicio'),
    path('registrar_clase/', RegistroClaseView.as_view(), name='registrar_clase'),
    path('obtener_informacion_clase/<str:codigo_clase>', obtener_informacion_clase, name='obtener_informacion_clase'),
    path('<str:codigo_clase>/', ConsultarClaseView.as_view(), name='ver_materia'),
    path('<str:codigo_clase>/_alumno', ConsultarClaseAlumnoView.as_view(), name='ver_materia_alumno'),
    path('unirse_a_clase/<str:codigo_clase>', SolicitarUnirseAClaseView.as_view(), name='unirse_a_clase'),
    path('<str:codigo_clase>/alumno/<int:id_alumno>/cambiar_estado_inscripcion',
         ModificarEstadoInscriocionAlumno.as_view(), name='cambiar_estado_inscripcion'),
    path('<str:codigo_clase>/grupo', ListarAlumnosDeClase.as_view(), name='grupo'),
    path('', include('apps.actividades.urls')),
    path('', include('apps.foros.urls')),
    path('', include('apps.avisos.urls'))
]
