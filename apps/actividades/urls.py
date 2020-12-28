from django.urls import path

from apps.actividades.views import consultar_actividades_de_clase, registrar_actividad, consultar_actividad, \
    revisar_entrega_actividad

urlpatterns = [
    path('<str:codigo_clase>/actividades/', consultar_actividades_de_clase, name='actividades'),
    path('<str:codigo_clase>/registro_actividad/', registrar_actividad, name='registrar_actividad'),
    path('<str:codigo_clase>/actividades/<int:id_actividad>', consultar_actividad, name='consultar_actividad_mestro'),
    path('<str:codigo_clase>/actividades/<int:id_actividad>/entregas/<int:id_entrega>', revisar_entrega_actividad,
         name='revisar_entrega')
]