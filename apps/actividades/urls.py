from django.urls import path

from apps.actividades.views import consultar_actividades_de_clase, registrar_actividad, consultar_actividad

urlpatterns = [
    path('<str:codigo_clase>/actividades/', consultar_actividades_de_clase, name='actividades'),
    path('<str:codigo_clase>/registro_actividad/', registrar_actividad, name='registrar_actividad'),
    path('<str:codigo_clase>/actividades/<int:id_actividad>', consultar_actividad, name='consultar_actividad_mestro')
]