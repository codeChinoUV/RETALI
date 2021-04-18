from django.urls import path

from apps.actividades.views import ConsultarActividadesDeClaseView, ConsultarActividadesDelAlumnoView, \
    RegistroActividadView, EditarActividadView, ConsultarActividadView, RevisarEntregaActividadView, \
    EntregarActividadView, DescargarArchivoView

urlpatterns = [
    path('<str:codigo_clase>/actividades', ConsultarActividadesDeClaseView.as_view(), name='actividades'),
    path('<str:codigo_clase>/actividades/alumno', ConsultarActividadesDelAlumnoView.as_view(), name='actividades_alumno'),
    path('<str:codigo_clase>/registro_actividad', RegistroActividadView.as_view(), name='registrar_actividad'),
    path('<str:codigo_clase>/actividades/<int:pk>/editar', EditarActividadView.as_view(), name='editar_actividad'),
    path('<str:codigo_clase>/actividades/<int:id_actividad>/', ConsultarActividadView.as_view(),
         name='consultar_actividad_mestro'),
    path('<str:codigo_clase>/actividades/<int:id_actividad>/entregas/<int:id_entrega>',
         RevisarEntregaActividadView.as_view(), name='revisar_entrega'),
    path('<str:codigo_clase>/actividades/<int:id_actividad>/entregar_actividad', EntregarActividadView.as_view(),
         name='entregar_actividad'),
    path('<str:codigo_clase>/actividades/<int:id_actividad>/entregas/<int:id_entrega>/descargar/<int:id_archivo>',
         DescargarArchivoView.as_view(), name='descargar_archivo_entrega')
]
