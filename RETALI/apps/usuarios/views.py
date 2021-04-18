from django.contrib.auth.decorators import login_required
from django.db import transaction, DatabaseError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.base import View

from apps.clases.models import Maestro, Alumno

from apps.usuarios.forms import UsuarioForm, PersonaForm, MaestroForm, AlumnoForm
from apps.usuarios.models import Usuario


def redireccion_path_vacio(request):
    """
    Redigere al usuario a la pagina principal o la pagina de inicio de sesion
    :param request: La solicitud del cliente
    :return: Redirect a la pagina indicada
    """
    if request.user.is_authenticated:
        return redirect('inicio')
    else:
        return redirect('inicio_sesion')


class RegistroView(View):
    """ Vista para registrar a un usuario """
    model = Usuario
    template_name = 'usuarios/registro-usuario/RegistroUsuario.html'
    form_class = UsuarioForm
    second_form_class = PersonaForm
    success_url = reverse_lazy('inicio_sesion')

    def get(self, request, *args, **kwargs):
        context = {}
        if 'formulario_usuario' not in context:
            context['formulario_usuario'] = UsuarioForm
        if 'formulario_persona' not in context:
            context['formulario_persona'] = PersonaForm
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        formulario_usuario = self.form_class(request.POST)
        formulario_persona = self.second_form_class(request.POST)
        context = {'formulario_usuario': formulario_usuario, 'formulario_persona': formulario_persona}
        if formulario_usuario.is_valid() and formulario_persona.is_valid():
            try:
                with transaction.atomic():
                    usuario = formulario_usuario.save()
                    if usuario.es_maestro:
                        persona = Maestro(usuario=usuario)
                        formulario_maestro = MaestroForm(request.POST, instance=persona)
                        formulario_maestro.is_valid()
                        formulario_maestro.save()
                    else:
                        persona = Alumno(usuario=usuario)
                        formulario_alumno = AlumnoForm(request.POST, instance=persona)
                        formulario_alumno.is_valid()
                        formulario_alumno.save()
                    messages.info(request, 'Se ha enviado un correo de verificación a ' + usuario.email)
                    return HttpResponseRedirect(self.success_url)
            except DatabaseError:
                messages.warning('Ocurrio un error y no se registro el usuario, intentelo nuevamente')
                return render(request, self.template_name, context)
        else:
            return render(request, self.template_name, context)


class InicioSesionView(View):
    """ Vista para iniciar sesion """
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('inicio')
        return render(request, 'usuarios/iniciar-sesion/Login.html')

    def post(self, request):
        correo = request.POST['username']
        contrasenia = request.POST['password']
        usuario = authenticate(request, username=correo, password=contrasenia)
        if usuario is not None:
            login(request, usuario)
            return redirect('inicio')
        else:
            messages.warning(request, 'El correo electronico o la contraseña son incorrectos')
            return render(request, 'usuarios/iniciar-sesion/Login.html')


class CierreSesionView(View):
    """ Vista para cerrar sesion """
    def get(self, request):
        logout(request)
        return redirect('inicio')


@method_decorator(login_required, name='dispatch')
class InicioView(View):
    """ Vista para mostrar la pagina de inicio de un usuario"""
    template_alumno = 'usuarios/pagina-inicio-alumno/PaginaInicioAlumno.html'
    template_maestro = 'usuarios/paginaInicio/PaginaInicioMaestro.html'

    def get(self, request):
        if request.user.es_maestro:
            return render(request, self.template_maestro)
        else:
            return render(request, self.template_alumno)
