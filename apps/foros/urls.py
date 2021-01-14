from django.urls import path

from apps.foros.views import consultar_foros_maestro

urlpatterns = [
    path('<str:codigo_clase>/foros', consultar_foros_maestro, name='foros'),

]
