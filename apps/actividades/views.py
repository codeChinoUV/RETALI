import datetime
import os
import pytz
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, HttpResponse
from django.utils import timezone
from RETALI import settings
from apps.actividades.forms import ActividadForm, ActividadDisableForm
from apps.actividades.models import Actividad, Entrega, Archivo, Revision
from apps.clases.models import Clase
from apps.clases.views import obtener_cantidad_de_alumnos_inscritos_a_clase


@login_required
def consultar_actividades_de_clase(request, codigo_clase):
    """
    Obtiene las actividades de una clase
    :param request: El request del cliente
    :param codigo_clase: El codigo de la clase de la cual se quiere obtener las actividades
    :return: Una template con sus datos o un redirect a la pagina correcta
    """
    if not request.user.es_maestro:
        return redirect('paginaInicio')
    else:
        datos_del_maestro = {}
        datos_del_maestro['clase_actual'] = request.user.persona.maestro.clase_set.filter(abierta=True,
                                                                                          codigo=codigo_clase).first()
        if datos_del_maestro['clase_actual'] is not None:
            datos_del_maestro['actividades'] = datos_del_maestro['clase_actual'].actividad_set.all() \
                .order_by('-fecha_de_creacion')
            _actualizar_estado_actividades(datos_del_maestro['actividades'])
            _colocar_cantidad_de_entregas_de_actividad(datos_del_maestro['actividades'])
            datos_del_maestro['total_alumnos'] = \
                obtener_cantidad_de_alumnos_inscritos_a_clase(datos_del_maestro['clase_actual'].id)
            datos_del_maestro['total_de_actividades'] = \
                obtener_cantidad_total_de_actividades(datos_del_maestro['clase_actual'])
            datos_del_maestro['cantidad_actividades_abiertas'] = \
                obtener_cantidad_de_actividades_abiertas(datos_del_maestro['actividades'])
            return render(request, 'actividades/consultar-actividades-maestro/ConsultarActividadesMaestro.html',
                          datos_del_maestro)


@login_required
def consultar_actividades_de_clase_alumno(request, codigo_clase):
    """
    Obtiene las actividades de una clase para el alumno
    :param request: El request del cliente
    :param codigo_clase: El codigo de la clase de la cual se quiere obtener las actividades
    :return: Una template con sus datos o un redirect a la pagina correcta
    """
    if request.user.es_maestro:
        return redirect('paginaInicio')
    else:
        alumno = request.user.persona.alumno
        clase = Clase.objects.filter(codigo=codigo_clase).first()
        inscripcion = alumno.inscripcion_set.filter(aceptado='Aceptado', clase_id=clase.id).first()
        datos_del_alumno = {}
        datos_del_alumno['clase_actual'] = inscripcion.clase
        if datos_del_alumno['clase_actual'] is not None:
            datos_del_alumno['actividades'] = datos_del_alumno['clase_actual'].actividad_set.all() \
                .order_by('-fecha_de_creacion')
            _actualizar_estado_actividades(datos_del_alumno['actividades'])
            datos_del_alumno['total_de_actividades'] = \
                obtener_cantidad_total_de_actividades(datos_del_alumno['clase_actual'])
            datos_del_alumno['cantidad_actividades_abiertas'] = \
                obtener_cantidad_de_actividades_abiertas(datos_del_alumno['actividades'])
            return render(request, 'actividades/consultar-actividades-alumno/ConsultarActividadesAlumno.html',
                          datos_del_alumno)


@login_required()
def registrar_actividad(request, codigo_clase):
    """
    Registra una actividad a la clase actual
    :param request: La solicitud realizada por el cliente
    :param codigo_clase: El codigo de la clase a la que se le registrara la actividad
    :return: Una templete con los datos
    """
    if not request.user.es_maestro:
        return redirect('paginaInicio')
    else:
        datos_del_maestro = {}
        datos_del_maestro['clase_actual'] = request.user.persona.maestro.clase_set. \
            filter(abierta=True, codigo=codigo_clase).first()
        if datos_del_maestro['clase_actual'] is not None:
            datos_del_maestro['form'] = ActividadForm()
            if request.method == "POST":
                formulario = ActividadForm(request.POST)
                if formulario.is_valid():
                    datos_de_la_actividad = formulario.cleaned_data
                    if validar_fecha_cierre_mayor_a_fecha_apertura(datos_de_la_actividad["fecha_inicio"],
                                                                   datos_de_la_actividad["fecha_cierre"]):
                        actividad = Actividad(nombre=datos_de_la_actividad['nombre'],
                                              descripcion=datos_de_la_actividad['descripcion'],
                                              fecha_de_inicio=datos_de_la_actividad['fecha_inicio'],
                                              fecha_de_cierre=datos_de_la_actividad['fecha_cierre'],
                                              clase_id=datos_del_maestro['clase_actual'].id)
                        actividad.save()
                        return redirect('actividades', codigo_clase=codigo_clase)
                    else:
                        formulario.errors["fecha_inicio"] = "La fecha de inicio no puede ser antes que la fecha " \
                                                            "de cierre"
                    datos_del_maestro['form'] = formulario
                    return render(request, 'actividades/registrar-actividad/RegistrarActividad.html', datos_del_maestro)
            else:
                return render(request, 'actividades/registrar-actividad/RegistrarActividad.html', datos_del_maestro)
        else:
            return render(request, 'generales/NoEncontrada.html', datos_del_maestro)


@login_required()
def editar_actividad(request, codigo_clase, id_actividad):
    """
    Edita una actividad
    :param request: La solicitud realizada por el cliente
    :param codigo_clase: El codigo de la clase a la que pertence la actividad a editar
    :return: Un render o un redirect
    """
    if request.user.es_maestro:
        datos_del_maestro = {}
        datos_del_maestro["clase_actual"] = request.user.persona.maestro.clase_set.filter(codigo=codigo_clase).first()
        if request.method == "GET":
            if datos_del_maestro["clase_actual"] is not None:
                if _validar_existe_actividad(codigo_clase, id_actividad, request.user.persona.maestro):
                    actividad_actual = Actividad.objects.filter(pk=id_actividad).first()
                    datos_del_maestro["form"] = _crear_formulario_con_informacion_de_actividad(actividad_actual)
                    return render(request, 'actividades/editar_actividad/EditarActividad.html', datos_del_maestro)
            return render(request, 'generales/NoEncontrada.html', datos_del_maestro)
        elif request.method == "POST":
            if datos_del_maestro["clase_actual"] is not None:
                if _validar_existe_actividad(codigo_clase, id_actividad, request.user.persona.maestro):
                    formulario = ActividadForm(request.POST)
                    if formulario.is_valid():
                        datos = formulario.cleaned_data
                        if validar_fecha_cierre_mayor_a_fecha_apertura(datos["fecha_inicio"], datos["fecha_cierre"]):
                            _actualizar_informacion_actividad(id_actividad, datos["nombre"], datos["descripcion"],
                                                              datos["fecha_inicio"], datos["fecha_cierre"])
                            return redirect('consultar_actividad_mestro', codigo_clase=codigo_clase,
                                            id_actividad=id_actividad)
                        else:
                            formulario.errors["fecha_inicio"] = "La fecha de inicio no puede ser antes que la fecha " \
                                                                "de cierre"
                    datos_del_maestro["form"] = formulario
                    return render(request, 'actividades/editar_actividad/EditarActividad.html', datos_del_maestro)
        raise Http404
    else:
        return redirect('paginaInicio')


def validar_fecha_cierre_mayor_a_fecha_apertura(fecha_inicio, fecha_cierre):
    """
    Valida que la fecha de inicio no sea mayor a la fecha de cierre
    :param fecha_inicio: La fecha de inicio
    :param fecha_cierre: La fecha de cierre
    :return: True si la fecha de cierre no es mayor a la fecha de inicio
    """
    return fecha_cierre > fecha_inicio


def _crear_formulario_con_informacion_de_actividad(actividad):
    """
    Crea un formulario de actividad con los datos de la actividad
    :param actividad: La actividad con la cual se llenaran los campos del formulario
    :return: Un ActividadForm con la informacion de la actividad
    """
    formulario = ActividadForm()
    formulario.fields["nombre"].initial = actividad.nombre
    formulario.fields["descripcion"].initial = actividad.descripcion
    formulario.fields["fecha_inicio"].initial = actividad.fecha_de_inicio
    formulario.fields["fecha_cierre"].initial = actividad.fecha_de_cierre
    return formulario


def _actualizar_informacion_actividad(id_actividad, nombre, descripcion, fecha_inicio, fecha_cierre):
    """
    Actualiza la informacion de la activdad con el id_actividad
    :param id_actividad: El id de la actividad a actualiazr sus datos
    :param nombre: El nombre de la actividad
    :param descripcion: La descripcion de la actividad
    :param fecha_inicio: La fecha de inicio de la actividad
    :param fecha_cierre: La fecha de cierre de la actividad
    :return: None
    """
    Actividad.objects.filter(pk=id_actividad).update(nombre=nombre, descripcion=descripcion,
                                                     fecha_de_inicio=fecha_inicio, fecha_de_cierre=fecha_cierre)


def _actualizar_estado_actividades(actividades):
    """
    Actualiza el estado de las actividades que se le pasan, verificando si esta abierta o no
    :param actividades: Las actividades a las que se le actualizara el estado
    :return: None
    """
    if actividades is not None:
        for actividad in actividades:
            _actualizar_estado_actividad(actividad)


def _actualizar_estado_actividad(actividad):
    """
    Actualiza el estado de una sola actividad dependiendo la fecha de cierre de esta
    :param actividad: La actividad a la cual se le actualiza el estado
    :return: None
    """
    now = timezone.now()
    if actividad.fecha_de_inicio > now:
        Actividad.objects.filter(pk=actividad.pk).update(estado='Por abrir')
        actividad.estado = 'Por abrir'
    elif actividad.fecha_de_cierre < now:
        Actividad.objects.filter(pk=actividad.pk).update(estado='Cerrada')
        actividad.estado = 'Cerrada'
    else:
        Actividad.objects.filter(pk=actividad.pk).update(estado='Abierta')
        actividad.estado = 'Abierta'


def _colocar_cantidad_de_entregas_de_actividad(actividades):
    """
    Coloca la cantidad de entregas en la actividad
    :param actividades: La lista de actividades
    :return: None
    """
    if actividades is not None:
        for actividad in actividades:
            actividad.cantidad_entregas = actividad.entrega_set.count()


def obtener_cantidad_de_actividades_abiertas(actividades):
    """
    Cuenta la cantidad de actividades que su fecha de entrega es despues de la fecha actual
    :param actividades: Las actividades a checar
    :return: La cantidad de actividades abiertas
    """
    now = timezone.now()
    cantidad_actividades_abiertas = 0
    for actividad in actividades:
        if actividad.fecha_de_cierre > now > actividad.fecha_de_inicio:
            cantidad_actividades_abiertas += 1
    return cantidad_actividades_abiertas


def obtener_cantidad_total_de_actividades(clase):
    """
    Cuenta la cantidad total de actividades de una clase
    :param clase: La clase de la cual se contaran las actividades
    :return: EL total de actividades de una clase
    """
    return clase.actividad_set.count()


@login_required()
def consultar_actividad(request, codigo_clase, id_actividad):
    """
    Muestra la informacion de la actividad con sus entregas
    :param request: La solicitud del cliente
    :param codigo_clase: El codigo de la clase a la que pertenece la actividad
    :param id_actividad: El id de la activdad a editar
    :return: un redirect o un render
    """
    if not request.user.es_maestro:
        return redirect('paginaInicio')
    else:
        datos_del_maestro = {}
        datos_del_maestro['clase_actual'] = request.user.persona.maestro.clase_set. \
            filter(codigo=codigo_clase, abierta=True).first()
        if _validar_existe_actividad(codigo_clase, id_actividad, request.user.persona.maestro):
            datos_del_maestro['actividad_actual'] = datos_del_maestro['clase_actual']. \
                actividad_set.filter(pk=id_actividad).first()
            datos_del_maestro['form'] = ActividadDisableForm()
            datos_del_maestro['entregas'] = datos_del_maestro['actividad_actual'].entrega_set.all()
            return render(request, 'actividades/consultar-actividad-maestro/consultarActividadMaestro.html',
                          datos_del_maestro)
        else:
            return render(request, 'generales/NoEncontrada.html', datos_del_maestro)


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


@login_required()
def revisar_entrega_actividad(request, codigo_clase, id_actividad, id_entrega):
    """
    Muestra un formulario para revisar la entrega a una actividad de un alumno
    :param request: La solicitud del cliente
    :param codigo_clase: El codigo de la clase a la que pertenece la actividad a revisar la entrega
    :param id_actividad: El id de la actividad a revisar la entrega
    :param id_entrega: El id de la entrega a revisar
    :return: Un redirec o un render
    """
    if not request.user.es_maestro:
        return redirect('paginaInicio')
    else:
        datos_del_maestro = {}
        datos_del_maestro['clase_actual'] = request.user.persona.maestro.clase_set. \
            filter(codigo=codigo_clase, abierta=True).first()
        if _validar_existe_entrega(codigo_clase, id_actividad, id_entrega, request.user.persona.maestro):
            datos_del_maestro = _colocar_informacion_de_la_actividad(datos_del_maestro, id_actividad, id_entrega)
            if request.method == 'GET':
                return render(request, 'actividades/revisar-entrega-actividad/RevisarEntregaActividad.html',
                              datos_del_maestro)
            elif request.method == 'POST':
                if not _validar_actividad_abierta(datos_del_maestro['actividad_actual']):
                    if request.POST.get('calificacion') is None or request.POST.get('calificacion') == '0':
                        datos_del_maestro['errores'] = {
                            'calificacion': 'Debe de escoger una calificacion'
                        }
                    else:
                        if datos_del_maestro['entrega_actual'].revision is not None:
                            _actualizar_revision(datos_del_maestro['revision'].pk,
                                                 request.POST['calificacion'], request.POST['comentarios'])
                        else:
                            _registrar_revision(datos_del_maestro['entrega_actual'], request.POST['calificacion'],
                                                request.POST['comentarios'], )
                        return redirect('consultar_actividad_mestro', codigo_clase=codigo_clase,
                                        id_actividad=id_actividad)
                else:
                    datos_del_maestro['errores'] = {
                        'fecha-cierre': 'No puede guardar su revisión hasta que la activdad se cierre'
                    }
                    return render(request, 'actividades/revisar-entrega-actividad/RevisarEntregaActividad.html',
                                  datos_del_maestro)
        else:
            return render(request, 'generales/NoEncontrada.html', datos_del_maestro)


def _colocar_informacion_de_la_actividad(datos_anteriores, id_actividad, id_entrega):
    """
    Coloca la información necesaria para desplegar la pagina de calificar actividad
    :param datos_anteriores: Los datos anteriores de la actividad
    :param id_actividad: El id de la actividad a revisar la entrega
    :param id_entrega: EL id de la entrega a revisar
    :return: Los datos actualizados
    """
    datos_anteriores['actividad_actual'] = datos_anteriores['clase_actual']. \
        actividad_set.filter(pk=id_actividad).first()
    datos_anteriores['form'] = ActividadDisableForm()
    datos_anteriores['entrega_actual'] = datos_anteriores['actividad_actual']. \
        entrega_set.filter(pk=id_entrega).first()
    datos_anteriores['archivos'] = datos_anteriores['entrega_actual'].archivo_set.all()
    if datos_anteriores['entrega_actual'].revision is not None:
        datos_anteriores['revision'] = datos_anteriores['entrega_actual'].revision
        datos_anteriores['revision'].calificacion = datos_anteriores['revision'].calificacion = \
            int(datos_anteriores['revision'].calificacion)
    return datos_anteriores


def _registrar_revision(entrega_actual, calificacion, comentarios):
    """
    Registra una revisión de una entrega de una actividad
    :param entrega_actual: La entrega a revisar
    :param calificacion: La calificación a guardar
    :param comentarios: Los comentarios de la actividad
    :return: None
    """
    revision = Revision(calificacion=calificacion,
                        retroalimentacion=comentarios)
    revision.save()
    Entrega.objects.filter(pk=entrega_actual.pk).update(revision=revision)


def _actualizar_revision(id_revision_actual, calificacion, comentarios):
    """
    Actualiza la infomración de una revisión previa
    :param id_revision_actual: El id de la revision
    :param calificacion: La calificación nueva
    :param comentarios: Los comentarios nuevos
    :return: None
    """
    Revision.objects.filter(pk=id_revision_actual). \
        update(calificacion=calificacion, retroalimentacion=comentarios)


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
            return redirect('paginaInicio')
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
    _actualizar_estado_actividad(actividad)
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
