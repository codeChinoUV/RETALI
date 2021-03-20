from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DetailView

from apps.clases.models import Clase, Inscripcion, EstadoSolicitudUnirse
from apps.foros.forms import ForoForm
from apps.foros.models import Foro, Participacion, Respuesta
from apps.usuarios.mixins import MaestroMixin, AlumnoMixin


class ListarForosMaestroView(MaestroMixin, ListView):
    """ Vista para consultar los foros de un maestro"""
    model = Foro
    template_name = 'foros/consultar-foros-maestro/ConsultarForosMaestro.html'

    def get_queryset(self):
        return Foro.objects.filter(clase__codigo=self.kwargs['codigo_clase'],
                                   clase__maestro_id=self.request.user.persona.maestro.pk).\
            order_by('-fecha_de_creacion')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ListarForosMaestroView, self).get_context_data(**kwargs)
        query_clase = Clase.objects.filter(codigo=self.kwargs['codigo_clase'])
        clase = get_object_or_404(query_clase, maestro_id=self.request.user.persona.maestro.pk)
        clase.actualizar_estado_foros()
        context['cantidad_foros_abiertos'] = clase.cantidad_de_foros_abiertos()
        context['total_de_foros'] = clase.cantidad_de_foros()
        return context


class ListarForosAlumnoView(AlumnoMixin, ListView):
    """ Vista para consultar los foros de un alumno"""
    model = Foro
    template_name = 'foros/consultar-foros-alumno/ConsultarForosAlumno.html'

    def get_queryset(self):
        return Foro.objects.filter(clase__codigo=self.kwargs['codigo_clase']).order_by('-fecha_de_creacion')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ListarForosAlumnoView, self).get_context_data(**kwargs)
        query_inscripcion = Inscripcion.objects.filter(clase__codigo=self.kwargs['codigo_clase'],
                                                       aceptado=EstadoSolicitudUnirse.ACEPTADO)
        inscripcion = get_object_or_404(query_inscripcion, alumno_id=self.request.user.persona.alumno.pk)
        inscripcion.clase.actualizar_estado_foros()
        context['cantidad_foros_abiertos'] = inscripcion.clase.cantidad_de_foros_abiertos()
        context['total_de_foros'] = inscripcion.clase.cantidad_de_foros()
        return context


class CrearForoView(MaestroMixin, CreateView):
    model = Foro
    form_class = ForoForm
    template_name = 'foros/registro-foro/RegistroForo.html'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object
        formulario = self.form_class(request.POST)
        if formulario.is_valid():
            query_clase = Clase.objects.filter(abierta=True)
            clase = get_object_or_404(query_clase, codigo=kwargs['codigo_clase'])
            formulario = formulario.save(commit=False)
            formulario.clase = clase
            formulario.save()
            messages.info(request, 'El foro se ha registrado correctamente')
            return redirect('foros', codigo_clase=kwargs['codigo_clase'])
        else:
            return self.render_to_response(self.get_context_data(form=formulario))


class ModificarForo(MaestroMixin, UpdateView):
    """Vista para modificar un foro"""
    model = Foro
    template_name = 'foros/editar-foro/EditarForo.html'
    form_class = ForoForm

    def get_context_data(self, **kwargs):
        context = super(ModificarForo, self).get_context_data(**kwargs)
        codigo_clase = self.kwargs['codigo_clase']
        id_foro = self.kwargs['pk']
        query_foro = Foro.objects.filter(clase__abierta=True, clase__codigo=codigo_clase,
                                         clase__maestro_id=self.request.user.persona.maestro.pk)
        foro = get_object_or_404(query_foro, pk=id_foro)
        if 'form' not in context:
            context['form'] = self.form_class(instance=foro)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object
        codigo_clase = self.kwargs['codigo_clase']
        id_foro = self.kwargs['pk']
        query_foro = Foro.objects.filter(clase__abierta=True, clase__codigo=codigo_clase,
                                         clase__maestro_id=self.request.user.persona.maestro.pk)
        foro = get_object_or_404(query_foro, pk=id_foro)
        formulario = self.form_class(request.POST, instance=foro)
        if formulario.is_valid():
            formulario.save()
            messages.info(request, 'Se ha modificado correctamente la información del foro ')
            return redirect('consultar_foro', codigo_clase=codigo_clase, id_foro=id_foro)
        else:
            return self.render_to_response(self.get_context_data(form=formulario))


class ConsultarForoView(LoginRequiredMixin, DetailView):
    """Vista para consultar el foro"""
    model = Foro
    template_name = 'foros/consultar-foro/ConsultarForo.html'

    def get_context_data(self, **kwargs):
        foro = get_object_or_404(Foro.objects, pk=self.kwargs['pk'])
        foro.actualizar_estado()
        return super(ConsultarForoView, self).get_context_data(**kwargs)


@login_required()
def participar_en_foro(request, codigo_clase, id_foro):
    """
    Registra una participacion en un foro
    :param request: La solictud del usuario
    :param codigo_clase: El codigo de la clase en donde pertence el foro
    :param id_foro: El id del foro al que se le registrara la participacion
    :return: un redirect
    """
    if request.method == "POST":
        if request.user.es_maestro:
            if _validar_existe_foro_maestro(request.user.persona.maestro, codigo_clase, id_foro):
                if request.POST['participacion'] is not None and request.POST['participacion'] != '':
                    _registrar_participacion(request.user.persona.pk, id_foro, request.POST['participacion'])
                    return redirect('consultar_foro', codigo_clase=codigo_clase, pk=id_foro)
        else:
            if _validar_existe_foro_alumno(request.user.persona.alumno, codigo_clase, id_foro):
                if request.POST['participacion'] is not None and request.POST['participacion'] != '':
                    _registrar_participacion(request.user.persona.pk, id_foro, request.POST['participacion'])
                    return redirect('consultar_foro', codigo_clase=codigo_clase, pk=id_foro)
    raise Http404


def _registrar_participacion(id_persona, id_foro, participacion):
    """
    Registra una nueva participacion de una persona en un foro
    :param id_persona: El id de la persona que realizo la participacion
    :param id_foro: El id del foro en donde se registrara la participacion
    :param participacion: La participación realizada
    :return: None
    """
    participacion = Participacion(participacion=participacion, participante_id=id_persona, foro_id=id_foro)
    participacion.save()


def _validar_existe_foro_maestro(maestro, codigo_clase, id_foro):
    """
    Valida si existe un foro en una clase en donde del maestro
    :param maestro: El maestro a validar si el foro pertence a alguna de sus clases
    :param codigo_clase: El codigo de la clase del foro
    :param id_foro: El id del foro a validar si existe
    :return: True si existe o False si no
    """
    existe_foro = False
    clase = Clase.objects.filter(codigo=codigo_clase).first()
    if clase is not None:
        clase = maestro.clase_set.filter(pk=clase.id).first()
        if clase is not None:
            if clase.foro_set.filter(eliminado=False, pk=id_foro).count() > 0:
                existe_foro = True
    return existe_foro


def _validar_existe_foro_alumno(alumno, codigo_clase, id_foro):
    """
    Valida si existe el foro en alguna clase en donde el alumno se encuentre inscrito
    :param alumno: El alumno a valiadr si el foro se encuentra en algunas de sus clases inscritas
    :param codigo_clase: El codigo de la clase del foro
    :param id_foro: El id del foro a validar si existe
    :return: True si el foro existe o False si no
    """
    existe_foro = False
    clase = Clase.objects.filter(codigo=codigo_clase).first()
    if clase is not None:
        inscripcion = alumno.inscripcion_set.filter(aceptado='Aceptado', clase_id=clase.pk).first()
        if inscripcion is not None:
            foro = inscripcion.clase.foro_set.filter(pk=id_foro).first()
            if foro is not None:
                existe_foro = True
    return existe_foro


@login_required()
def responder_participacion(request, codigo_clase, id_foro, id_participacion):
    """
    Registra una respuesta a una participacion
    :param codigo_clase: El codigo de la clase en donde se encuentra el foro de la participacion a responder
    :param id_foro: El id del foro de la participacion
    :param id_participacion: El id de la participacion a responder
    :return: un redirect
    """
    if request.method == "POST":
        if request.user.es_maestro:
            if _validar_existe_participacion_foro_maestro(request.user.persona.maestro, codigo_clase, id_foro,
                                                          id_participacion):
                if request.POST['respuesta'] is not None and request.POST['respuesta'] != '':
                    _registrar_respuesta(request.user.persona.pk, id_participacion, request.POST['respuesta'])
                    return redirect('consultar_foro', codigo_clase=codigo_clase, pk=id_foro)
        else:
            if _validar_existe_participacion_foro_alumno(request.user.persona.alumno, codigo_clase, id_foro,
                                                         id_participacion):
                if request.POST['respuesta'] is not None and request.POST['respuesta'] != '':
                    _registrar_respuesta(request.user.persona.pk, id_participacion, request.POST['respuesta'])
                    return redirect('consultar_foro', codigo_clase=codigo_clase, pk=id_foro)
    raise Http404


def _validar_existe_participacion_foro_alumno(alumno, codigo_clase, id_foro, id_participacion):
    """
    Valida si existe una participacion en un foro
    :param alumno: El alumno que va responder a la participacion
    :param codigo_clase: El codigo de la clase en donde se encuentra el foro
    :param id_foro: El id del foro
    :param id_participacion: El id de la participacion
    :return: True si existe la participacion o False si no
    """
    existe_participacion = False
    if _validar_existe_foro_alumno(alumno, codigo_clase, id_foro):
        if Participacion.objects.filter(pk=id_participacion, eliminada=False).count() > 0:
            existe_participacion = True
    return existe_participacion


def _validar_existe_participacion_foro_maestro(maestro, codigo_clase, id_foro, id_participacion):
    """
    Valida si existe una participacion en un foro
    :param maestro: El maestro que va a responder a la participacion
    :param codigo_clase: El codigo de la clase en donde se encuentra el foro
    :param id_foro: El id del foro a validar si existe
    :param id_participacion: El id de la participacion a validar si existe
    :return: True si existe el comentario o False si no
    """
    existe_participacion = False
    if _validar_existe_foro_maestro(maestro, codigo_clase, id_foro):
        if Participacion.objects.filter(pk=id_participacion, eliminada=False).count() > 0:
            existe_participacion = True
    return existe_participacion


def _registrar_respuesta(id_persona, id_participacion, respuesta):
    """
    Registra una respuesta a una participacion
    :param id_persona: El id de la persona que realizo la participacion
    :param id_participacion: El id de la participacion a responder
    :param respuesta: La respuesta
    :return: None
    """
    respuesta_anteriores = Respuesta.objects.filter(participacion_id=id_participacion).count()
    respuesta_actual = respuesta_anteriores + 1
    respuesta = Respuesta(autor_id=id_persona, participacion_id=id_participacion, respuesta=respuesta,
                          numero_respuesta=respuesta_actual)
    respuesta.save()
