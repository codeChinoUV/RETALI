from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.views import View
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


class ParticiparEnForoView(LoginRequiredMixin, View):
    """ Vista para guardar la participación de una persona en un foro"""
    @staticmethod
    def _validar_participacion(participacion):
        return participacion is not None and participacion != ''

    def post(self, request, codigo_clase, id_foro):
        if request.user.es_maestro:
            query_foro = Foro.objects.filter(clase__codigo=codigo_clase, clase__abierta=True,
                                             clase__maestro_id=request.user.persona.maestro.pk)
            foro = get_object_or_404(query_foro, pk=id_foro)
        else:
            query_inscripcion = Inscripcion.objects.filter(clase__codigo=codigo_clase, clase__abierta=True,
                                                           aceptado=EstadoSolicitudUnirse.ACEPTADO)
            inscripcion = get_object_or_404(query_inscripcion, alumno_id=request.user.persona.alumno.pk)
            query_foro = inscripcion.clase.foro_set
            foro = get_object_or_404(query_foro, pk=id_foro)
        foro.actualizar_estado()
        if self._validar_participacion(request.POST['participacion']) and foro.estado == 'Abierta':
            foro.registrar_participacion(request.POST['participacion'], request.user.persona.pk)
            messages.info(request, 'Su participación se ha registrado correctamente')
        else:
            messages.warning('Su participación no se ha guardado, verifique si el foro aun se encuentra abierto')
        return redirect('consultar_foro', codigo_clase=codigo_clase, pk=id_foro)


class ResponderParticipacionView(LoginRequiredMixin, View):
    """Vista para responder a una participación"""
    @staticmethod
    def _validar_respuesta(respuesta):
        return respuesta is not None and respuesta != ''

    def post(self, request, codigo_clase, id_foro, id_participacion):
        if request.user.es_maestro:
            query_foro = Foro.objects.filter(clase__codigo=codigo_clase, clase__abierta=True,
                                             clase__maestro_id=request.user.persona.maestro.pk)
            foro = get_object_or_404(query_foro, pk=id_foro)
        else:
            query_inscripcion = Inscripcion.objects.filter(clase__codigo=codigo_clase, clase__abierta=True,
                                                           aceptado=EstadoSolicitudUnirse.ACEPTADO)
            inscripcion = get_object_or_404(query_inscripcion, alumno_id=request.user.persona.alumno.pk)
            query_foro = inscripcion.clase.foro_set
            foro = get_object_or_404(query_foro, pk=id_foro)
        query_participacion = foro.participacion_set.filter(eliminada=False)
        participacion = get_object_or_404(query_participacion, pk=id_participacion)
        foro.actualizar_estado()
        if self._validar_respuesta(request.POST['respuesta']) and foro.estado == 'Abierta':
            participacion.registrar_respuesta(request.POST['respuesta'], request.user.persona.pk)
            messages.info(request, 'Su respuesta se ha registrado correctamente')
        else:
            messages.warning('Su respuesta no se ha guardado, verifique si el foro aun se encuentra abierto')
        return redirect('consultar_foro', codigo_clase=codigo_clase, pk=id_foro)
