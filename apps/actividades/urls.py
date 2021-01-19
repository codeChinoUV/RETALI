from django.urls import path

from apps.actividades.views import consultar_actividades_de_clase, registrar_actividad, consultar_actividad, \
    revisar_entrega_actividad, entregar_actividad_alumno, descargar_archivo_de_entrega,  editar_actividad, consultar_actividades_de_clase_alumno

urlpatterns = [
    path('<str:codigo_clase>/actividades', consultar_actividades_de_clase, name='actividades'),
    path('<str:codigo_clase>/actividades/alumno', consultar_actividades_de_clase_alumno, name='actividades_alumno'),
    path('<str:codigo_clase>/registro_actividad', registrar_actividad, name='registrar_actividad'),
    path('<str:codigo_clase>/actividades/<int:id_actividad>/editar', editar_actividad, name='editar_actividad'),
    path('<str:codigo_clase>/actividades/<int:id_actividad>/', consultar_actividad, name='consultar_actividad_mestro'),
    # path('<str:codigo_clase>/actividades/<int:id_actividad>/alumno', consultar_actividad_alumno, name='consultar_actividad_alumno'),
    path('<str:codigo_clase>/actividades/<int:id_actividad>/entregas/<int:id_entrega>', revisar_entrega_actividad,
         name='revisar_entrega'),
    path('<str:codigo_clase>/actividades/<int:id_actividad>/entregar_actividad', entregar_actividad_alumno,
         name='entregar_actividad'),
    path('<str:codigo_clase>/actividades/<int:id_actividad>/entregas/<int:id_entrega>/descargar/<int:id_archivo>',
         descargar_archivo_de_entrega, name='descargar_archivo_entrega')
]
