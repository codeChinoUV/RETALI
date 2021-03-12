import random

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView
from django.views.generic.base import View

from .forms import ClaseForm
from .models import Clase, Inscripcion, EstadoSolicitudUnirse


@method_decorator(login_required, name='dispatch')
class RegistroClaseView(CreateView):
    model = Clase
    form_class = ClaseForm
    success_url = reverse_lazy('inicio')
    template_name = 'clases/registro-clase/RegistroClase.html'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object
        formulario = self.form_class(request.POST, request.FILES)
        if formulario.is_valid():
            clase = formulario.save(commit=False)
            clase.maestro_id = request.user.persona.maestro.pk
            clase.codigo = Clase.obtener_codigo_unico()
            clase.save()
            return HttpResponseRedirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=formulario))


@login_required()
def informacion_clase(request, codigo_clase):
    """
    Recupera la información de la clase de un maestro
    :param request: La solicitud del cliente
    :param codigo_clase: El codigo de la clase a obtener la informacion
    :return: Un redirect o un render
    """
    if not request.user.es_maestro:
        return redirect('login')
    else:
        maestro = request.user.persona.maestro
        clase_actual = maestro.clase_set.filter(abierta=True, codigo=codigo_clase).first()
        datos = {}
        if clase_actual is not None:
            return render(request, 'clases/informacion-clase/InformacionClase.html', datos)
        else:
            return render(request, 'generales/NoEncontrada.html', datos)


def obtener_cantidad_de_alumnos_inscritos_a_clase(id_clase):
    """
    Obtiene la cantidad de alumnos inscritos a una clase
    :param id_clase: El id de la clase
    :return: La cantidad de alumnos aceptados en la clase
    """
    return Clase.objects.filter(pk=id_clase).first().inscripcion_set.filter(aceptado='Aceptado').count()


@login_required()
def obtener_informacion_clase(request, codigo_clase):
    """
    Responde a una solicitud AJAX con la información de una clase
    :param request: La solicitud del usuario
    :param codigo_clase: El codigo de la clase de la cual se devolvera la informacion
    :return: Un JSON con la informacion del maestro
    """
    if request.is_ajax and request.method == "GET":
        clase_con_codigo = Clase.objects.filter(codigo=codigo_clase, abierta=True).first()
        if clase_con_codigo is not None:
            datos = _crearJSONClase(clase_con_codigo)
            return JsonResponse(datos)
        else:
            return JsonResponse({'error': 'No exite ninguna clase con el codigo indicado'})
    raise Http404


def _crearJSONClase(clase):
    """
    Crea un Diccionario con los datos de una clase
    :param clase: La clase de la cual se creara la clase
    :return: Un diccionario con la información de la clase
    """
    url_foto_maeestro = ''
    if clase.maestro.foto_de_perfil:
        url_foto_maeestro = clase.maestro.foto_de_perfil.url
    datos_clase = {
        'nombre': clase.nombre,
        'escuela': clase.escuela,
        'foto': clase.foto.url,
        'maestro': clase.maestro.nombre + ' ' + clase.maestro.apellidos,
        'foto_maestro': url_foto_maeestro
    }
    return datos_clase


# Falta protección a la ruta
@method_decorator(login_required, name='dispatch')
class ListarAlumnosDeClase(ListView):
    model = Inscripcion
    template_name = 'usuarios/consultar-alumnos-de-clase/ConsultarAlumnosDeClase.html'
    queryset = Inscripcion.objects.select_related('alumno')
    ordering = 'alumno__nombre'

    def get_queryset(self):
        clase_actual = self.kwargs['codigo_clase']
        return Inscripcion.objects.filter(clase__codigo=clase_actual).select_related('alumno')


# Falta proteccion de la ruta
@method_decorator(login_required, name='dispatch')
class ModificarEstadoInscriocionAlumno(View):

    def post(self, request, codigo_clase, id_alumno):
        queryset = request.user.persona.maestro.clase_set.filter(abierta=True)
        clase_actual = get_object_or_404(queryset, codigo=codigo_clase)
        if _validar_opcion_existente_inscripcion(request.POST['estado']):
            clase_actual.modificar_estado_inscripcion_alumno(id_alumno, request.POST['estado'])
            return redirect('grupo', codigo_clase=codigo_clase)
        raise Http404


def _validar_opcion_existente_inscripcion(estado):
    """
    Valida si el estado se encuentra en la lista de estados validos
    :param estado: El estado a validar
    :return: True si se encuentra o False si no
    """
    estados = EstadoSolicitudUnirse.values
    return estado in estados


@login_required()
def unir_alumno_a_clase(request, codigo_clase):
    """
    Une un alumno a una clase al crear una inscripcion
    :param request: La solicitud del usuario
    :param codigo_clase: El codigo de la clase a la que el alumno se quiere unir
    :return: Un JSON
    """
    if not request.user.es_maestro:
        if request.is_ajax and request.method == 'GET':
            mensaje_error = _validar_inscripcion_a_clase(request.user.persona.alumno, codigo_clase)
            if mensaje_error == "":
                _registrar_inscripcion_alumno(request.user.persona.alumno.pk, codigo_clase)
                return JsonResponse({})
            else:
                return JsonResponse({'error': mensaje_error})
    raise Http404


def _registrar_inscripcion_alumno(id_alumno, codigo_clase):
    """
    Registra un alumno en una clase
    :param id_alumno: El id del alumno a inscribir en una clase
    :param codigo_clase: El codigo de la clase en la cual el alumno se va a unir
    :return: None
    """
    clase = Clase.objects.filter(codigo=codigo_clase, abierta=True).first()
    inscripcion = Inscripcion(clase_id=clase.pk, alumno_id=id_alumno)
    inscripcion.save()


def _validar_inscripcion_a_clase(alumno, codigo_clase):
    """
    Valida si existe una inscripcion previa del alumno
    :param alumno: El alumno a validar sus inscripciones
    :param codigo_clase: El codigo de la clase a validar
    :return: Un mensaje correspondiente al error
    """
    mensaje_error = "La clase a la que se desea inscribir no existe"
    clase = Clase.objects.filter(abierta=True, codigo=codigo_clase).first()
    if clase is not None:
        inscripcion = alumno.inscripcion_set.filter(clase_id=clase.pk).first()
        if inscripcion is not None:
            if inscripcion.estado == 'Aceptado':
                mensaje_error = "Ya se encuentra inscrito a esta clase"
            elif inscripcion.estado == 'Rechazado':
                mensaje_error = "El maestro de la clase rechazo su solicitud para unirse a la clase"
            else:
                mensaje_error = "El maestro aun no revisa su solicitud para unirse a la clase"
        else:
            mensaje_error = ""
    return mensaje_error


@login_required()
def informacion_clase_alumno(request, codigo_clase):
    """
    Muestra la informacion de una clase para el usuario alumno
    :param request: La solicitud del usuario
    :param codigo_clase: El codigo de la clase a mostrar la informacion
    :return: Un render o un redirect
    """
    if request.user.es_maestro:
        return redirect('login')
    else:
        alumno = request.user.persona.alumno
        clase = Clase.objects.filter(codigo=codigo_clase).first()
        inscripcion = alumno.inscripcion_set.filter(aceptado='Aceptado', clase_id=clase.id).first()
        clase_actual = inscripcion.clase
        datos = {}
        if clase_actual is not None:
            datos['clase_actual'] = clase_actual
            return render(request, 'clases/informacion-clase/InformacionClaseAlumno.html', datos)
        else:
            return render(request, 'generales/NoEncontrada.html', datos)


def contar_estados_inscripciones_de_alumnos(alumnos_de_la_clase, datos_cantidad_alumnos):
    pass

