from django.urls import path

from apps.foros.views import consultar_foro, participar_en_foro, responder_participacion, \
    editar_foro, ListarForosMaestroView, ListarForosAlumnoView, CrearForoView

urlpatterns = [
    path('<str:codigo_clase>/foros', ListarForosMaestroView.as_view(), name='foros'),
    path('<str:codigo_clase>/foros/alumno', ListarForosAlumnoView.as_view(), name='foros_alumno'),
    path('<str:codigo_clase>/foros/registrar_foro', CrearForoView.as_view(), name='registro_foro'),
    path('<str:codigo_clase>/foros/<int:id_foro>/editar', editar_foro, name='editar_foro'),
    path('<str:codigo_clase>/foros/<int:id_foro>', consultar_foro, name='consultar_foro'),
    path('<str:codigo_clase>/foros/<int:id_foro>/registrar_participacion', participar_en_foro,
         name='registrar_participacion'),
    path('<str:codigo_clase>/foros/<int:id_foro>/participaciones/<int:id_participacion>/responder',
         responder_participacion, name='responder_participacion')
]
