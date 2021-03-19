import os

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, TemplateView

from RETALI import settings
from apps.actividades.forms import ActividadForm, ActividadDisableForm
from apps.actividades.models import Actividad, Entrega, Archivo
from apps.clases.models import Clase, Inscripcion
from apps.usuarios.mixins import MaestroMixin, AlumnoMixin


class ConsultarActividadesDeClaseView(MaestroMixin, ListView):
    """Muestra las actividades de una clase para la vista del maestro"""
    template_name = 'actividades/consultar-actividades-maestro/ConsultarActividadesMaestro.html'
    model = Actividad

    def get_queryset(self):
        clase_actual = self.kwargs['codigo_clase']
        return Actividad.objects.filter(clase__codigo=clase_actual, clase__abierta=True).order_by('-fecha_de_creacion')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ConsultarActividadesDeClaseView, self).get_context_data(**kwargs)
        query_set = Clase.objects.filter(abierta=True)
        clase_actual = get_object_or_404(query_set, codigo=self.kwargs['codigo_clase'])
        clase_actual.actualizar_estado_actividades()
        context['total_de_alumnos'] = clase_actual.obtener_cantidad_de_alumnos_aceptados()
        context['total_de_actividades'] = clase_actual.cantidad_de_actividades()
        context['cantidad_actividades_abiertas'] = clase_actual.cantidad_de_actividades_abiertas()
        return context


class ConsultarActividadesDelAlumnoView(AlumnoMixin, ListView):
    """Muestra las actividades de una clase para la vista del alumno"""
    model = Actividad
    template_name = 'actividades/consultar-actividades-alumno/ConsultarActividadesAlumno.html'

    def get_queryset(self):
        clase_actual = self.kwargs['codigo_clase']
        return Actividad.objects.filter(clase__codigo=clase_actual, clase__abierta=True).order_by('-fecha_de_creacion')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ConsultarActividadesDelAlumnoView, self).get_context_data(**kwargs)
        query_set = Clase.objects.filter(abierta=True)
        clase_actual = get_object_or_404(query_set, codigo=self.kwargs['codigo_clase'])
        clase_actual.actualizar_estado_actividades()
        context['total_de_actividades'] = clase_actual.cantidad_de_actividades()
        context['cantidad_actividades_abiertas'] = clase_actual.cantidad_de_actividades_abiertas()
        return context


class RegistroActividadView(MaestroMixin, CreateView):
    """Vista para registrar una actividad"""
    model = Actividad
    template_name = 'actividades/registrar-actividad/RegistrarActividad.html'
    form_class = ActividadForm

    def post(self, request, *args, **kwargs):
        self.object = self.get_object
        formulario = self.form_class(request.POST)
        if formulario.is_valid():
            query_clase = Clase.objects.filter(abierta=True)
            clase = get_object_or_404(query_clase, codigo=kwargs['codigo_clase'])
            actividad = formulario.save(commit=False)
            actividad.clase = clase
            actividad.save()
            messages.info(request, 'La actividad se ha registrado correctamente')
            return redirect('actividades', codigo_clase=kwargs['codigo_clase'])
        else:
            return self.render_to_response(self.get_context_data(form=formulario))


class EditarActividadView(MaestroMixin, UpdateView):
    """Vista para editar una actividad"""
    model = Actividad
    template_name = 'actividades/editar_actividad/EditarActividad.html'
    form_class = ActividadForm

    def get_context_data(self, **kwargs):
        context = super(EditarActividadView, self).get_context_data(**kwargs)
        codigo_clase = self.kwargs['codigo_clase']
        id_actividad = self.kwargs['pk']
        query_set_actividad = Actividad.objects.filter(clase__abierta=True, clase__codigo=codigo_clase)
        actividad = get_object_or_404(query_set_actividad, pk=id_actividad)
        if 'form' not in context:
            context['form'] = self.form_class(instance=actividad)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        codigo_clase = kwargs['codigo_clase']
        id_actividad = kwargs['pk']
        query_set_actividad = Actividad.objects.filter(clase__abierta=True, clase__codigo=codigo_clase)
        actividad = get_object_or_404(query_set_actividad, pk=id_actividad)
        formulaio = self.form_class(request.POST, instance=actividad)
        if formulaio.is_valid():
            formulaio.save()
            messages.info(request, 'Se ha modificado la información de la actividad correctamente')
            return redirect('consultar_actividad_mestro', codigo_clase=codigo_clase, id_actividad=id_actividad)
        else:
            return self.render_to_response(self.get_context_data(form=formulaio))


class ConsultarActividadView(MaestroMixin, TemplateView):
    """ Vista para consultar actividad y sus entregas"""
    template_name = 'actividades/consultar-actividad-maestro/consultarActividadMaestro.html'

    def get_context_data(self, **kwargs):
        context = super(ConsultarActividadView, self).get_context_data(**kwargs)
        codigo_clase = kwargs['codigo_clase']
        id_actividad = kwargs['id_actividad']
        query_set_actividad = Actividad.objects.filter(clase__abierta=True, clase__codigo=codigo_clase,
                                                       clase__maestro_id=self.request.user.persona.maestro.pk)
        actividad = get_object_or_404(query_set_actividad, pk=id_actividad)
        actividad.actualizar_estado_actividad()
        context['form'] = ActividadDisableForm(instance=actividad)
        context['id_actividad'] = id_actividad
        context['entregas'] = actividad.entrega_set.all()
        return context


def _validar_existe_actividad(codigo_clase, id_actividad, maestro):
    """
    Valida si existe la actividad indicada dentro de la clase indicada del maestro
    :param codigo_clase: EL codigo de la clase de la cual se va a buscar la actividad
    :param id_actividad: EL id de la actividad a validar si existe
    :param maestro: El maestro de donde se sacaran las clases
    :return: True si la actividad existe, False si no
    """
    if maestro.clase_set.filter(codigo=codigo_clase, abierta=True).count() > 0:
        clase = maestro.clase_set.filter(codigo=codigo_clase, abierta=True).first()
        if clase.actividad_set.filter(pk=id_actividad) is not None:
            return True
    return False


class RevisarEntregaActividadView(MaestroMixin, View):
    """ Vista para revisar una actividad"""
    template = 'actividades/revisar-entrega-actividad/RevisarEntregaActividad.html'

    @staticmethod
    def _validar_informacion_revision_incorrecta(calificacion, comentarios):
        return comentarios is None or calificacion == '0'

    def get_context_data(self, request, codigo_clase, id_actividad, id_entrega):
        context = {}
        query_entrega = Entrega.objects.filter(actvidad__clase__maestro_id=request.user.persona.maestro.pk,
                                               actvidad_id=id_actividad).select_related('revision')
        query_actividad = Actividad.objects.filter(clase__maestro_id=request.user.persona.maestro.pk,
                                                   clase__codigo=codigo_clase,
                                                   clase__abierta=True)
        context['actividad'] = get_object_or_404(query_actividad, pk=id_actividad)
        context['entrega'] = get_object_or_404(query_entrega, pk=id_entrega)
        context['archivos'] = context['entrega'].archivo_set.all()
        return context

    def get(self, request, codigo_clase, id_actividad, id_entrega):
        context = self.get_context_data(request, codigo_clase, id_actividad, id_entrega)
        return render(request, self.template, context)

    def post(self, request, codigo_clase, id_actividad, id_entrega):
        context = self.get_context_data(request, codigo_clase, id_actividad, id_entrega)
        if not context['actividad_actual'].esta_abierta():
            if not self._validar_informacion_revision_incorrecta(request.POST['calificacion'],
                                                                 request.POST['comentarios']):
                context['entrega'].realizar_revision(request.POST['calificacion'], request.POST['comentarios'])
                messages.info(request, 'Se ha registrado la revisión a la actividad de ' +
                              context['entrega'].alumno.nombre)
                return redirect('consultar_actividad_mestro', codigo_clase=codigo_clase, id_actividad=id_actividad)
            else:
                messages.warning(request, 'La información de la revisión no es correcta, verifique e '
                                          'intentelo de nuevo')
        else:
            messages.warning(request, 'No puede evaluar una actividad mientras esta siga abierta')
        return render(request, self.template, context)


def _validar_existe_entrega(codigo_clase, id_actividad, id_entrega, maestro):
    """
    Valida si existe la entrega en la clase y la actividad señaladas
    :param codigo_clase: El codigo de la clase
    :param id_actividad: El id de la actividad
    :param id_entrega: El id de la entrega
    :param maestro: El maestro actual
    :return: True si existe la entrega o False si no
    """
    existe_entrega = False
    if _validar_existe_actividad(codigo_clase, id_actividad, maestro):
        if maestro.clase_set.filter(abierta=True, codigo=codigo_clase).first().actividad_set. \
                filter(pk=id_actividad).first().entrega_set.filter(pk=id_entrega).count() > 0:
            existe_entrega = True
    return existe_entrega


class EntregarActividadView(AlumnoMixin, View):
    template = 'actividades/entregar-actividad-alumno/EntregarActividadAlumno.html'

    @staticmethod
    def _validar_es_maestro(es_maestro):
        """
        Valdia si un usuario es maestro
        :param es_maestro: El parametro que indica si es maestro
        :return: Un diccionario con un error si el usuario es un Maestro o None si no lo es
        """
        if es_maestro:
            return {'error': 'Un maestro no puede entregar una actividad'}

    @staticmethod
    def _validar_informacion_entrega(comentarios, archivos):
        """
        Valida si la información de una entrega es correcta
        :param comentarios: Los comentarios de la entrega
        :param archivos: Los archivos de la entrega
        """
        if not (comentarios is not None or len(archivos) > 0):
            return {'error': 'Debe de adjuntar por lo menos un archivo o escribir algun comentario'}

    @staticmethod
    def _validar_existe_actividad(id_alumno, codigo_clase, id_actividad):
        """
        Valida si existe una entrega
        :param id_alumno: El id del alumno a validar si esta inscrito en la clase
        :param codigo_clase: El codigo de la clase a la que pertence la actividad
        :param id_actividad: El id de la actividad a validar si existe
        :return: None si la actividad existe o un diccionario con el error si no
        """
        error = {'error': 'No existe la actividad que se desea entregar'}
        inscripcion = Inscripcion.objects.filter(clase__codigo=codigo_clase, alumno_id=id_alumno,
                                                 aceptado='Aceptado').select_related('clase').first()
        if inscripcion is None:
            return error
        if inscripcion.clase.actividad_set.filter(pk=id_actividad).count() == 0:
            return error

    @staticmethod
    def _validar_actividad_abierta(id_actividad):
        """
        Valida si una actividad se encuentra abierta
        :param id_actividad: El id de la actividad a validar
        :return: Un diccionario con un error si no se encuentra abierta o None si se encuentra cerrada
        """
        actividad = Actividad.objects.filter(pk=id_actividad).first()
        if not actividad.esta_abierta():
            return {'error': 'La actividad ha cerrrado y no se entrego'}

    @staticmethod
    def _validar_tamanio_archivo(archivo):
        """
        Valida si un archivo supera los 50MB de tamaño
        :param archivo: El archivo a validar
        :return: True si es menor a el tamaño maximo o False si no
        """
        tamano_maximo = 51068760  # 50MB
        es_valido = True
        if archivo.size > tamano_maximo:
            es_valido = False
        return es_valido

    @staticmethod
    def _validar_tamanio_archivos(archivos):
        """
        Valida si los archivos adjuntos no superan los 50MB de tamaño
        :param archivos: Los archivos a validar
        :return: True si todos los archivos no superan el tamaño valido o False si no
        """
        son_validos = True
        for archivo in archivos.items():
            if not EntregarActividadView._validar_tamanio_archivo(archivo[1]):
                son_validos = False
                break
        if not son_validos:
            return {'error': 'Cada archivo no debe de ser mas grande de 50KB'}

    @staticmethod
    def _validar_entrega(archivos, comentarios, id_alumno, codigo_clase, id_actividad):
        """
        Realiza todas las validaciones de una entrega
        :param archivos: Los archivos de la entrega
        :param comentarios: Los comentarios de la entrega
        :param id_alumno: El id del alumno que realizo la entrega
        :param codigo_clase: El codigo de la clase al que pertenece la actividad
        :param id_actividad: El id de la actividad a entregar
        :return: Un diccionario si hubo un problema en la validación o None si no hubo errores
        """
        error = EntregarActividadView._validar_existe_actividad(id_alumno, codigo_clase, id_actividad)
        if error is not None:
            return error
        error = EntregarActividadView._validar_actividad_abierta(id_actividad)
        if error is not None:
            return error
        error = EntregarActividadView._validar_informacion_entrega(comentarios, archivos)
        if error is not None:
            return error
        error = EntregarActividadView._validar_tamanio_archivos(archivos)
        if error is not None:
            return error

    def get_context(self, request, codigo_clase, id_actividad):
        context = {}
        query_set_inscripcion = Inscripcion.objects.filter(clase__codigo=codigo_clase, clase__abierta=True)
        inscripcion = get_object_or_404(query_set_inscripcion, alumno_id=request.user.persona.alumno.pk)
        query_set_actividad = inscripcion.clase.actividad_set
        context['actividad'] = get_object_or_404(query_set_actividad, pk=id_actividad)
        context['entrega'] = Entrega.objects.filter(alumno_id=request.user.persona.alumno.pk,
                                                    actvidad_id=id_actividad).first()
        if context['entrega'] is not None:
            context['archivos'] = context['entrega'].archivo_set.all()
        return context

    def get(self, request, codigo_clase, id_actividad):
        context = self.get_context(request, codigo_clase, id_actividad)
        return render(request, self.template, context)

    def post(self, request, codigo_clase, id_actividad):
        error_entrega = self._validar_entrega(request.FILES, request.POST['comentarios'],
                                              request.user.persona.alumno.pk, codigo_clase, id_actividad)
        if error_entrega is not None:
            return JsonResponse(error_entrega, status=400)
        actividad = Actividad.objects.filter(pk=id_actividad).first()
        actividad.realizar_entrega(self.request.user.persona.alumno.pk, request.POST['comentarios'], request.FILES)
        return JsonResponse({}, status=200)


class DescargarArchivoView(LoginRequiredMixin, View):
    """ Vista para descargar un archivo"""
    @staticmethod
    def _obtener_archivo(ruta_archivo):
        """
        Obtiene el archivo del disco y lo regresa al usuario
        :param ruta_archivo: La ruta del archivo a obtener
        :return: HttpResponse
        """
        if os.path.exists(ruta_archivo):
            with open(ruta_archivo, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/octet-stream")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(ruta_archivo)
                return response

    def get(self, request, codigo_clase, id_actividad, id_entrega, id_archivo):
        """
        Responde una salicitud get al devolver el archivo de la una entrega
        :param request: La solicitud del usuario
        :param codigo_clase: El codigo de la clase a la que pertenece la actividad
        :param id_actividad: El id de la actividad a la que pertenence la entrega
        :param id_entrega: El id de la entrega a la que pertenence el archivo
        :param id_archivo: El id del archivo a descargar
        :return: Un HttpResponse
        """
        archivo = Archivo.objects.filter(pk=id_archivo).first()
        if archivo is not None:
            file_path = os.path.join(settings.MEDIA_ROOT, archivo.archivo.path)
            if request.user.es_maestro:
                query_actividad = Actividad.objects.filter(clase__codigo=codigo_clase, clase__abierta=True,
                                                           clase__maestro_id=request.user.persona.maestro.pk)
                actividad = get_object_or_404(query_actividad, pk=id_actividad)
                query_entrega = actividad.entrega_set
                get_object_or_404(query_entrega, pk=id_entrega)
                return self._obtener_archivo(file_path)
            else:
                query_inscripcion = Inscripcion.objects.filter(aceptado='Aceptado', clase__codigo=codigo_clase)
                inscripcion = get_object_or_404(query_inscripcion, alumno_id=request.user.persona.alumno.pk)
                query_actividad = inscripcion.clase.actividad_set
                actividad = get_object_or_404(query_actividad, pk=id_actividad)
                query_entrega = actividad.entrega_set
                get_object_or_404(query_entrega, pk=id_entrega)
                return self._obtener_archivo(file_path)
