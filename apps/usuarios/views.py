from django.contrib.auth.decorators import login_required
from django.db import transaction, DatabaseError
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic.base import View

from apps.clases.models import Inscripcion, Clase, Maestro, Alumno

from apps.usuarios.forms import UsuarioForm, PersonaForm, MaestroForm, AlumnoForm
from apps.usuarios.models import Usuario, Persona


def redireccion_path_vacio(request):
    """
    Redigere al usuario a la pagina principal o la pagina de inicio de sesion
    :param request: La solicitud del cliente
    :return: Redirect a la pagina indicada
    """
    if request.user.is_authenticated:
        return redirect('paginaInicio')
    else:
        return redirect('inicio_sesion')


class RegistroView(View):
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
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('paginaInicio')
        return render(request, 'usuarios/iniciar-sesion/Login.html')

    def post(self, request):
        correo = request.POST['username']
        contrasenia = request.POST['password']
        usuario = authenticate(request, username=correo, password=contrasenia)
        if usuario is not None:
            login(request, usuario)
            return redirect('paginaInicio')
        else:
            messages.warning(request, 'El correo electronico o la contraseña son incorrectos')
            return render(request, 'usuarios/iniciar-sesion/Login.html')


class CierreSesionView(View):
    def get(self, request):
        logout(request)
        return redirect('paginaInicio')


@login_required
def pagina_inicio(request):
    """
    Renderiza la pagina de inicio del maestro o del alumno
    :param request: La solictud del cliente
    :return: Un render de la pagina adecuada
    """
    if request.user.es_maestro:
        return render(request, 'usuarios/paginaInicio/PaginaInicioMaestro.html')
    else:
        return render(request, 'usuarios/pagina-inicio-alumno/PaginaInicioAlumno.html')



@login_required()
def consultar_alumnos_de_clases(request, codigo_clase):
    """
    Muestra la informacion de los alumnos que se encuentran inscritos a una clase
    :param request: La solicitud del usuario
    :param codigo_clase: El codigo de la clase a mostrar sus inscripciones
    :return: Un render
    """
    if request.method == "GET":
        datos_del_maestro = {}
        if _validar_existe_clase_maestro(request.user.persona.maestro, codigo_clase):
            datos_del_maestro["clase_actual"] = Clase.objects.filter(abierta=True, codigo=codigo_clase).first()
            datos_del_maestro["alumnos"] = obtener_alumnos_inscritos_a_clase(datos_del_maestro["clase_actual"])
            contar_estados_inscripciones_de_alumnos(datos_del_maestro["alumnos"], datos_del_maestro)
            return render(request, 'usuarios/consultar-alumnos-de-clase/ConsultarAlumnosDeClase.html',
                          datos_del_maestro)
        return render(request, 'generales/NoEncontrada.html', datos_del_maestro)
    raise Http404


def obtener_alumnos_inscritos_a_clase(clase):
    """
    Recupera los alumnos de una clase y los devuelve con el estado de su inscripcion
    :param clase: La clase de donde se tomaran los alumnos
    :return: Una lista de alumnos
    """
    inscripciones = clase.inscripcion_set.all()
    alumnos = []
    if inscripciones is not None:
        for inscripcion in inscripciones:
            alumno = inscripcion.alumno
            alumno.estado_inscripcion = inscripcion.aceptado
            alumnos.append(alumno)
        alumnos.sort(key=lambda x: x.apellidos)
    return alumnos


def _validar_existe_clase_maestro(maestro, codigo_clase):
    """
    Valida que exista una clase del alumno
    :param maestro: El maestro de a validr que la clase tenga la clase con el codigo
    :param codigo_clase: El codigo de la clase a validar si existe
    :return: True si la clase existe o False si no
    """
    existe_la_clase = False
    clase = Clase.objects.filter(codigo=codigo_clase).first()
    if clase is not None:
        if maestro.clase_set.filter(abierta=True, pk=clase.pk).count() > 0:
            existe_la_clase = True
    return existe_la_clase


@login_required()
def cambiar_estado_inscripcion_alumno(request, codigo_clase, id_alumno):
    """
    Cambia el estado de una inscripcion de un alumno
    :param request: La solicitud del usuario
    :param codigo_clase: El codigo de la clase de la inscripcion del alumno
    :param id_alumno: El id del alumno a cambiar el estado de su inscripcion
    :return: Un redirect
    """
    if request.method == "POST":
        if request.user.es_maestro:
            if _validar_existe_inscripcion(id_alumno, codigo_clase):
                if _validar_opcion_existente_inscripcion(request.POST['estado']):
                    _actualizar_estado_inscripcion_alumno(codigo_clase, id_alumno, request.POST['estado'])
                    return redirect('grupo', codigo_clase=codigo_clase)
    raise Http404


def _actualizar_estado_inscripcion_alumno(codigo_clase, id_alumno, estado_nuevo):
    """
    Actualiza el estado de la inscripcion de un alumno
    :param estado_nuevo:
    :param codigo_clase: El codigo de la clase de la inscripcion a actualizar
    :param id_alumno: El id del alumno de actualizar el estado de su inscripción
    :return: None
    """
    clase = Clase.objects.filter(codigo=codigo_clase).first()
    Inscripcion.objects.filter(alumno_id=id_alumno, clase_id=clase.pk).update(aceptado=estado_nuevo)


def _validar_opcion_existente_inscripcion(estado):
    """
    Valida si el estado se encuentra en la lista de estados validos
    :param estado: El estado a validar
    :return: True si se encuentra o False si no
    """
    estados = ["En espera", "Aceptado", "Rechazado"]
    return estado in estados


def _validar_existe_inscripcion(id_alumno, codigo_clase):
    """
    Valida si existe una inscripcion
    :param id_alumno: El id del alumno a validar si existe la inscripcion
    :param codigo_clase: El codigp de la clase a validar si existe en la inscripcion
    :return: True si existe la inscripcion o False si no
    """
    existe_inscripcion = False
    clase = Clase.objects.filter(codigo=codigo_clase).first()
    if clase is not None:
        existe_inscripcion = Inscripcion.objects.filter(alumno_id=id_alumno, clase_id=clase.pk).count() > 0
    return existe_inscripcion
