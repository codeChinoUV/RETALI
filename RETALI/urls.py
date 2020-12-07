"""RETALI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from apps.usuarios.views import iniciar_sesion, pagina_inicio, cerrar_sesion, registrar_usuario
from apps.clases.views import registrar_clase

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuario/', include('apps.usuarios.urls')),
    path('clases/', include('apps.clases.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
