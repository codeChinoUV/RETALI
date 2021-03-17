from django.urls import path

from apps.actividades.views import revisar_entrega_actividad, entregar_actividad_alumno, descargar_archivo_de_entrega, \
    ConsultarActividadesDeClaseView, ConsultarActividadesDelAlumnoView, RegistroActividadView, EditarActividadView, \
    ConsultarActividadView

urlpatterns = [
    path('<str:codigo_clase>/actividades', ConsultarActividadesDeClaseView.as_view(), name='actividades'),
    path('<str:codigo_clase>/actividades/alumno', ConsultarActividadesDelAlumnoView.as_view(), name='actividades_alumno'),
    path('<str:codigo_clase>/registro_actividad', RegistroActividadView.as_view(), name='registrar_actividad'),
    path('<str:codigo_clase>/actividades/<int:pk>/editar', EditarActividadView.as_view(), name='editar_actividad'),
    path('<str:codigo_clase>/actividades/<int:id_actividad>/', ConsultarActividadView.as_view(),
         name='consultar_actividad_mestro'),
    # path('<str:codigo_clase>/actividades/<int:id_actividad>/alumno', consultar_actividad_alumno, name='consultar_actividad_alumno'),
    path('<str:codigo_clase>/actividades/<int:id_actividad>/entregas/<int:id_entrega>', revisar_entrega_actividad,
         name='revisar_entrega'),
    path('<str:codigo_clase>/actividades/<int:id_actividad>/entregar_actividad', entregar_actividad_alumno,
         name='entregar_actividad'),
    path('<str:codigo_clase>/actividades/<int:id_actividad>/entregas/<int:id_entrega>/descargar/<int:id_archivo>',
         descargar_archivo_de_entrega, name='descargar_archivo_entrega')
]
