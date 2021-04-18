from django.urls import path

from apps.usuarios.views import RegistroView, InicioSesionView, CierreSesionView

urlpatterns = [
    path('iniciar_sesion/', InicioSesionView.as_view(), name='inicio_sesion'),
    path('cerrar_sesion/', CierreSesionView.as_view(), name='cerrarSesion'),
    path('registro/', RegistroView.as_view(), name='registro'),
]
