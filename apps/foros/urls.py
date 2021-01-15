from django.urls import path

from apps.foros.views import consultar_foros_maestro, registrar_foro

urlpatterns = [
    path('<str:codigo_clase>/foros', consultar_foros_maestro, name='foros'),
    path('<str:codigo_clase>/foros/registrar_foro', registrar_foro, name='registro_foro')

]
