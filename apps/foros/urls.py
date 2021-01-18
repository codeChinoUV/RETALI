from django.urls import path

from apps.foros.views import consultar_foros_maestro, registrar_foro, consultar_foro, participar_en_foro, \
    responder_participacion, editar_foro

urlpatterns = [
    path('<str:codigo_clase>/foros', consultar_foros_maestro, name='foros'),
    path('<str:codigo_clase>/foros/registrar_foro', registrar_foro, name='registro_foro'),
    path('<str:codigo_clase>/foros/<int:id_foro>/editar', editar_foro, name='editar_foro'),
    path('<str:codigo_clase>/foros/<int:id_foro>', consultar_foro, name='consultar_foro'),
    path('<str:codigo_clase>/foros/<int:id_foro>/registrar_participacion', participar_en_foro,
         name='registrar_participacion'),
    path('<str:codigo_clase>/foros/<int:id_foro>/participaciones/<int:id_participacion>/responder',
         responder_participacion, name='responder_participacion')
]
