from django.urls import path

from apps.foros.views import responder_participacion, ListarForosMaestroView, ListarForosAlumnoView, CrearForoView, \
    ModificarForo, ConsultarForoView, ParticiparEnForoView

urlpatterns = [
    path('<str:codigo_clase>/foros', ListarForosMaestroView.as_view(), name='foros'),
    path('<str:codigo_clase>/foros/alumno', ListarForosAlumnoView.as_view(), name='foros_alumno'),
    path('<str:codigo_clase>/foros/registrar_foro', CrearForoView.as_view(), name='registro_foro'),
    path('<str:codigo_clase>/foros/<int:pk>/editar', ModificarForo.as_view(), name='editar_foro'),
    path('<str:codigo_clase>/foros/<int:pk>', ConsultarForoView.as_view(), name='consultar_foro'),
    path('<str:codigo_clase>/foros/<int:id_foro>/registrar_participacion', ParticiparEnForoView.as_view(),
         name='registrar_participacion'),
    path('<str:codigo_clase>/foros/<int:id_foro>/participaciones/<int:id_participacion>/responder',
         responder_participacion, name='responder_participacion')
]
