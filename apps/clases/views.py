from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from django.views.generic.base import View, TemplateView

from .forms import ClaseForm
from .models import Clase, Inscripcion, EstadoSolicitudUnirse
from ..usuarios.mixins import MaestroMixin, AlumnoMixin


class RegistroClaseView(MaestroMixin, CreateView):
    """Vista para registrar una clase"""
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


class ConsultarClaseView(MaestroMixin, TemplateView):
    """Vista para consultar la información de una clase"""
    template_name = 'clases/informacion-clase/InformacionClase.html'

    def get_context_data(self, **kwargs):
        context = super(ConsultarClaseView, self).get_context_data(**kwargs)
        query_set = Clase.objects.filter(abierta=True)
        clase_actual = get_object_or_404(query_set, codigo=kwargs['codigo_clase'])
        context['alumnos_aceptados'] = clase_actual.obtener_cantidad_de_alumnos_aceptados()
        context['alumnos_en_espera'] = clase_actual.obtener_cantidad_de_alumnos_pendientes_de_aceptar()
        return context


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
            datos = clase_con_codigo.obtener_json()
            return JsonResponse(datos)
        else:
            return JsonResponse({'error': 'No exite ninguna clase con el codigo indicado'})
    raise Http404


class ListarAlumnosDeClase(MaestroMixin, ListView):
    """Vista para consultar los alumnos de una clase"""
    model = Inscripcion
    template_name = 'usuarios/consultar-alumnos-de-clase/ConsultarAlumnosDeClase.html'
    queryset = Inscripcion.objects.select_related('alumno')
    ordering = 'alumno__nombre'

    def get_queryset(self):
        clase_actual = self.kwargs['codigo_clase']
        return Inscripcion.objects.filter(clase__codigo=clase_actual).select_related('alumno')


class ModificarEstadoInscriocionAlumno(MaestroMixin, View):
    """Visra para modificar el estado de una inscripcion de un alumno"""
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


class SolicitarUnirseAClaseView(AlumnoMixin, View):
    """Vista para solicitar unirse a una clase"""
    def get(self, request, codigo_clase):
        mensaje_error = _validar_inscripcion_a_clase(request.user.persona.alumno, codigo_clase)
        if mensaje_error == "":
            clase = Clase.objects.filter(codigo=codigo_clase).first()
            clase.registrar_inscripcion_alumno(request.user.persona.alumno.pk)
            return HttpResponse(status=200)
        else:
            return JsonResponse({'error': mensaje_error}, status=400)


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


class ConsultarClaseAlumnoView(AlumnoMixin, TemplateView):
    """Vista para consultar la clase"""
    template_name = 'clases/informacion-clase/InformacionClaseAlumno.html'
