from django.urls import path

from apps.usuarios.views import iniciar_sesion, cerrar_sesion, registrar_usuario

urlpatterns = [
    path('iniciar_sesion/', iniciar_sesion, name='login'),
    path('cerrar_sesion/', cerrar_sesion, name='cerrarSesion'),
    path('registro/', registrar_usuario, name='registro'),
]