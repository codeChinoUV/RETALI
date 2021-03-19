from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, CreateView

from apps.avisos.forms import AvisoForm
from apps.avisos.models import Aviso
from apps.clases.models import Clase, Inscripcion
from apps.usuarios.mixins import MaestroMixin, AlumnoMixin


class ListarAvisosMaestroView(MaestroMixin, ListView):
    """ Vista para listar los avisos de un maestro"""
    template_name = 'avisos/consultar-avisos/ConsultarAvisos.html'
    model = Aviso

    def get_queryset(self):
        codigo_clase = self.kwargs['codigo_clase']
        return Aviso.objects.filter(clase__codigo=codigo_clase,
                                    clase__maestro_id=self.request.user.persona.maestro.pk)\
            .order_by('-fecha_publicado')


class ListarAvisosAlumnoView(AlumnoMixin, ListView):
    """ Vista para listar avisos de un alumno"""
    template_name = 'avisos/consultar-avisos-alumno/ConsultarAvisosAlumno.html'
    model = Aviso

    def get_queryset(self):
        codigo_clase = self.kwargs['codigo_clase']
        inscripcion = Inscripcion.objects.filter(clase__codigo=codigo_clase, aceptado='Aceptado').first()
        return inscripcion.clase.aviso_set.order_by('-fecha_publicado')


class CrearAvisoView(MaestroMixin, CreateView):
    """ Vista para crear un aviso"""
    model = Aviso
    form_class = AvisoForm
    template_name = 'avisos/registrar-aviso/RegistrarAviso.html'

    def post(self, request, *args, **kwargs):
        formulario = self.form_class(request.POST)
        if formulario.is_valid():
            query_clase = Clase.objects.filter(abierta=True)
            clase = get_object_or_404(query_clase, codigo=kwargs['codigo_clase'])
            aviso = formulario.save(commit=False)
            aviso.clase = clase
            aviso.save()
            messages.info(request, 'El aviso se ha creado correctamente')
            return redirect('avisos', codigo_clase=kwargs['codigo_clase'])
        else:
            return self.render_to_response(self.get_context_data(form=formulario))
