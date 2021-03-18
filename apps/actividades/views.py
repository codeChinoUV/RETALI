import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, TemplateView

from RETALI import settings
from apps.actividades.forms import ActividadForm, ActividadDisableForm
from apps.actividades.models import Actividad, Entrega, Archivo, Revision
from apps.clases.models import Clase
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
        context['actividad_actual'] = get_object_or_404(query_actividad, pk=id_actividad)
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


@login_required()
def entregar_actividad_alumno(request, codigo_clase, id_actividad):
    """
    Muestra una pagina para que el alumno pueda realizar una entrega a una actividad
    :param request: La solicitud del cliente
    :param codigo_clase: El codigo de la clase a la que pertenece la actividad a realizar la entrega
    :param id_actividad: El id de la actividad a entregar
    :return: un HttpResponse o un redirect o un render
    """
    if request.method == "POST":
        if request.user.es_maestro:
            return HttpResponse(status=500)
        else:
            codigo_revision_entrega = _validar_entrega_actividad(request.user.persona.alumno, codigo_clase,
                                                                 id_actividad, request.POST['comentarios'],
                                                                 request.FILES)
            if codigo_revision_entrega == 200:
                if _validar_existe_entrega_previa(request.user.persona.alumno, codigo_clase, id_actividad):
                    _actualizar_entrega(request.user.persona.alumno, id_actividad, request.POST['comentarios'],
                                        request.FILES)
                else:
                    _registrar_entrega(request.user.persona.alumno, id_actividad, request.POST['comentarios'],
                                       request.FILES)
            return HttpResponse(status=codigo_revision_entrega)
    elif request.method == "GET":
        if request.user.es_maestro:
            return redirect('inicio')
        else:
            if _validar_existe_actividad_de_alumno(codigo_clase, id_actividad, request.user.persona.alumno):
                clase = Clase.objects.filter(abierta=True, codigo=codigo_clase).first()
                datos_del_alumno = dict(
                    clase_actual=request.user.persona.alumno.inscripcion_set.filter(aceptado='Aceptado',
                                                                                    clase_id=clase.pk).first().clase)
                datos_del_alumno['actividad_actual'] = datos_del_alumno['clase_actual'].actividad_set.filter(
                    pk=id_actividad).first()
                if _validar_existe_entrega_previa(request.user.persona.alumno, codigo_clase, id_actividad):
                    datos_del_alumno['entrega'] = Entrega.objects.filter(alumno_id=request.user.persona.alumno.pk,
                                                                         actvidad_id=id_actividad).first()
                    datos_del_alumno['entrega_archivos'] = datos_del_alumno['entrega'].archivo_set.all()
                return render(request, 'actividades/entregar-actividad-alumno/EntregarActividadAlumno.html',
                              datos_del_alumno)
            return render(request, 'generales/NoEncontrada.html')


def validar_existe_actividad_alumno(codigo_clase, id_actividad, alumno):
    """
    Valida si existe la actividad en las clases inscriptas del alumno
    :param codigo_clase: El codigo de la clase a la que pertenece a la actividad
    :param id_actividad: El id de la actividdad a validar si existe
    :param alumno: El alumno a validar
    :return: True si la actividad existe o False si no
    """
    existe_actividad = False
    clase = Clase.objects.filter(codigo=codigo_clase).first()
    clase = alumno.inscripcion_set.filter(clase_id=clase.pk).first()
    if clase is not None:
        actividad = clase.actividad_set.filter(pk=id_actividad).first()
        if actividad is not None:
            existe_actividad = True
    return existe_actividad


def _validar_existe_entrega_previa(alumno, codigo_clase, id_actividad):
    """
    Actualiza la entrega previa con la nueva entrega
    :param alumno: El alumno que entrega la actividad
    :param codigo_clase: El codigo de la clase en donde se encuentra la actividad
    :param id_actividad: La actividad en donde se revisara si ya se entrego
    :return: True si existe una entrega previa o False si no
    """
    existe_entrega = False
    clase = Clase.objects.filter(codigo=codigo_clase).first()
    inscripcion = alumno.inscripcion_set.filter(clase_id=clase.pk).first()
    if inscripcion is not None:
        actividad = inscripcion.clase.actividad_set.filter(pk=id_actividad).first()
        if actividad is not None:
            if Entrega.objects.filter(actvidad_id=id_actividad, alumno_id=alumno.pk).count() > 0:
                existe_entrega = True
    return existe_entrega


def _registrar_entrega(alumno, id_actividad, comentarios, archivos):
    """
    Crea una entrega de un Alumno con sus Archivos adjuntos
    :param alumno: El alumno que entrego la actividad
    :param id_actividad: El id de la activdad de la entrega
    :param comentarios: Los comentarios de la entrega
    :param archivos: Los archivos adjuntos
    :return: None
    """
    entrega = Entrega(alumno_id=alumno.pk, actvidad_id=id_actividad, comentarios=comentarios)
    entrega.save()
    for archivo in archivos.values():
        archivo_entrega = Archivo(entrega_id=entrega.pk, archivo=archivo)
        archivo_entrega.save()


def _actualizar_entrega(alumno, id_actividad, comentarios, archivos):
    """
    Actualiza la entrega previa que habia del alumno
    :param alumno: El alumno que realizo la entrega
    :param id_actividad: El id de la actividad a la que se realizara la entrega
    :param comentarios: Los nuevos comentarios
    :param archivos: Los nuevos archivos
    :return: None
    """
    entrega = Entrega.objects.filter(alumno_id=alumno.pk, actvidad_id=id_actividad).first()
    archivos_entrega_previa = entrega.archivo_set.all()
    for archivo in archivos_entrega_previa:
        archivo.delete()
    Entrega.objects.filter(alumno_id=alumno.pk, actvidad_id=id_actividad).update(comentarios=comentarios)
    for archivo in archivos.values():
        archivo_entrega = Archivo(entrega_id=entrega.pk, archivo=archivo)
        archivo_entrega.save()


def _validar_entrega_actividad(alumno, codigo_clase, id_actividad, comentarios, archivos):
    """
    Valida que los datos de la entrega sean correctos, valida si la actividad existe, se encuentra abierta y si los
    archivos no superan el tamaño maximo
    :param alumno: El alumno que realizara la entrega
    :param codigo_clase: El codigo de la clase de la actividad
    :param id_actividad: El id de la actividad a la cual se realizara la entrega
    :param comentarios: Los comentarios de la entrega
    :param archivos: Los archivos adjuntos de la entrega
    :return: El codiogo correspondiente al estado de la actividad
    """
    # Codigo 400 La actividad no tiene archivos adjuntos ni comentarios
    # Codigo 401 La actividad se encuentra cerrada o todavia no abre
    # Codigo 402 Los archivos de la actividad superan los 50 MB
    # Codigo 403 No existe la actividad
    estado_actividad = 400
    if _validar_existe_actividad_de_alumno(codigo_clase, id_actividad, alumno):
        actividad = Actividad.objects.filter(pk=id_actividad).first()
        if _validar_actividad_abierta(actividad):
            if comentarios is not None and comentarios != "" or len(archivos) > 0:
                if _validar_tamanio_archivos(archivos):
                    estado_actividad = 200
                else:
                    estado_actividad = 402
        else:
            estado_actividad = 401
    else:
        estado_actividad = 403
    return estado_actividad


def _validar_actividad_abierta(actividad):
    """
    Valida si la actividad se encuentra abierta
    :param actividad: La actividad a validad
    :return: True si la actividad se encuentra abierta o False si no
    """
    esta_abierta = True
    #_actualizar_estado_actividad(actividad)
    if actividad.estado != 'Abierta':
        esta_abierta = False
    return esta_abierta


def _validar_tamanio_archivos(archivos):
    """
    Valida si los archivos adjuntos no superan los 50MB de tamaño
    :param archivos: Los archivos a validar
    :return: True si todos los archivos no superan el tamaño valido o False si no
    """
    son_validos = True
    for archivo in archivos.items():
        if not _validar_tamanio_archivo(archivo[1]):
            son_validos = False
            break
    return son_validos


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


def _validar_existe_actividad_de_alumno(codigo_clase, id_actividad, alumno):
    """
    Valida su existe una actividad para el alumno
    :param codigo_clase: El codigo de la clase a la cual pertenece la actividad
    :param id_actividad: El id de la actividad a entregar
    :param alumno: El alumno que realizara la entrega
    :return: True si existe la actividad o False si no
    """
    existe_actividad = False
    clase = Clase.objects.filter(abierta=True, codigo=codigo_clase).first()
    if clase is not None:
        clase_del_alumno = alumno.inscripcion_set.filter(aceptado='Aceptado', clase_id=clase.pk).first().clase
        if clase_del_alumno is not None:
            if clase_del_alumno.actividad_set.filter(pk=id_actividad).count() > 0:
                existe_actividad = True
    return existe_actividad


@login_required()
def descargar_archivo_de_entrega(request, codigo_clase, id_actividad, id_entrega, id_archivo):
    """
    Valida si el usuario es el maestro correspondiente de la entrega que contiene el archivo
    :param request: El request
    :param codigo_clase: El codigo de la clase de la actividad
    :param id_actividad: El id de la activdad de la entrega
    :param id_entrega: El id de la entrega
    :param id_archivo: El id del archivo a descargar
    :return: HttpResponse con el archivo
    """
    archivo = Archivo.objects.filter(pk=id_archivo).first()
    if archivo is not None:
        file_path = os.path.join(settings.MEDIA_ROOT, archivo.archivo.path)
        if request.user.es_maestro:
            if _validar_existe_actividad(codigo_clase, id_actividad, request.user.persona.maestro):
                if Entrega.objects.filter(pk=id_entrega).count() > 0:
                    return _obtener_archivo(file_path)
        else:
            if _validar_existe_actividad_de_alumno(codigo_clase, id_actividad, request.user.persona.alumno):
                if Entrega.objects.filter(pk=id_entrega).count() > 0:
                    return _obtener_archivo(file_path)

    raise Http404


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
