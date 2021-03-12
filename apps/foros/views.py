import datetime

import pytz
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from django.utils import timezone

from apps.actividades.views import validar_fecha_cierre_mayor_a_fecha_apertura
from apps.clases.models import Clase
from apps.foros.forms import ForoForm
from apps.foros.models import Foro, Participacion, Respuesta


@login_required
def consultar_foros_maestro(request, codigo_clase):
    """
    Muestra la informacion de los foros que tiene registrada una clase para el usuario maestro
    :param request: La solicitud del usuario
    :param codigo_clase: El codigo de la clase a mostrar sus foros
    :return: un render
    """
    if request.method == "GET":
        if request.user.es_maestro:
            datos_del_maestro = {}
            datos_del_maestro["clase_actual"] = request.user.persona.maestro.clase_set.filter(
                codigo=codigo_clase).first()
            if datos_del_maestro["clase_actual"] is not None:
                datos_del_maestro["foros"] = datos_del_maestro["clase_actual"].foro_set.filter(eliminado=False).all(). \
                    order_by('-fecha_de_creacion')
                _colocar_cantidad_participaciones_de_foro(datos_del_maestro["foros"])
                datos_del_maestro["cantidad_foros_abiertos"] = contar_foros_activos(datos_del_maestro["foros"])
                datos_del_maestro["total_de_foros"] = len(datos_del_maestro["foros"])
                return render(request, 'foros/consultar-foros-maestro/ConsultarForosMaestro.html', datos_del_maestro)
            else:
                return render(request, 'generales/NoEncontrada.html', datos_del_maestro)
    raise Http404


@login_required
def consultar_foros_alumno(request, codigo_clase):
    """
    Muestra la informacion de los foros que tiene registrada una clase para el usuario alumno
    :param request: La solicitud del usuario
    :param codigo_clase: El codigo de la clase a mostrar sus foros
    :return: un render
    """
    if request.method == "GET":
        if not request.user.es_maestro:
            alumno = request.user.persona.alumno
            clase = Clase.objects.filter(codigo=codigo_clase).first()
            inscripcion = alumno.inscripcion_set.filter(aceptado='Aceptado', clase_id=clase.id).first()
            datos_del_alumno = {}
            datos_del_alumno['clase_actual'] = inscripcion.clase
            if datos_del_alumno['clase_actual'] is not None:
                datos_del_alumno["foros"] = datos_del_alumno['clase_actual'].foro_set.filter(eliminado=False).all(). \
                    order_by('-fecha_de_creacion')
                _colocar_cantidad_participaciones_de_foro(datos_del_alumno["foros"])
                datos_del_alumno["cantidad_foros_abiertos"] = contar_foros_activos(datos_del_alumno["foros"])
                datos_del_alumno["total_de_foros"] = len(datos_del_alumno["foros"])
                return render(request, 'foros/consultar-foros-alumno/ConsultarForosAlumno.html', datos_del_alumno)
            else:
                return render(request, 'generales/NoEncontrada.html', datos_del_alumno)
    raise Http404


def _colocar_cantidad_participaciones_de_foro(foros):
    """
    Cuenta la cantidad de participaciones en un foro y las coloca en el objeto
    :param foros: Los foros a colocar la cantidad de particicpaciones
    :return: None
    """
    if foros is not None:
        for foro in foros:
            foro.cantidad_participaciones = foro.participacion_set.filter(eliminada=False).count()


def _actualizar_estado_foro(foro):
    """
    Actualiza el estado de un foro
    :param foro: El foro a actualizar su estado
    :return: None
    """
    now = timezone.now()
    if foro.fecha_de_inicio > now:
        Foro.objects.filter(pk=foro.pk).update(estado='Por abrir')
        foro.estado = 'Por abrir'
    elif foro.fecha_de_cierre < now:
        Foro.objects.filter(pk=foro.pk).update(estado='Cerrada')
        foro.estado = 'Cerrada'
    else:
        Foro.objects.filter(pk=foro.pk).update(estado='Abierta')
        foro.estado = 'Abierta'


def _actualizar_estado_foros(foros):
    """
    Actualiza el estado de todos los foros
    :param foros: Los foros a actualizar su estado
    :return: None
    """
    for foro in foros:
        _actualizar_estado_foro(foro)


def contar_foros_activos(foros):
    """
    Cuenta la cantidad de foros activos
    :param foros:
    :return:
    """
    _actualizar_estado_foros(foros)
    cantidad_abiertos = 0
    for foro in foros:
        if foro.estado == 'Abierta':
            cantidad_abiertos += 1
    return cantidad_abiertos


@login_required()
def registrar_foro(request, codigo_clase):
    """
    Muestra la plantila para registrar un nuevo foro en una clase
    :param request: La solcitud del usuario
    :param codigo_clase: El codigo de la clase en donde se va a registrar el foro
    :return: un render o un redirect
    """
    if request.user.es_maestro:
        datos_del_maestro = {}
        datos_del_maestro["clase_actual"] = request.user.persona.maestro.clase_set.filter(
            codigo=codigo_clase).first()
        if request.method == "GET":
            if datos_del_maestro["clase_actual"] is not None:
                datos_del_maestro["form"] = ForoForm()
                return render(request, 'foros/registro-foro/RegistroForo.html', datos_del_maestro)
            else:
                return render(request, 'generales/NoEncontrada.html', datos_del_maestro)
        elif request.method == "POST":
            formulario = ForoForm(request.POST)
            if formulario.is_valid():
                foro = formulario.cleaned_data
                if validar_fecha_cierre_mayor_a_fecha_apertura(foro["fecha_inicio"], foro["fecha_cierre"]):
                    _registrar_foro(datos_del_maestro["clase_actual"].pk, foro["nombre"], foro["descripcion"],
                                    foro["fecha_inicio"], foro["fecha_cierre"])
                    return redirect('foros', codigo_clase=codigo_clase)
                formulario.errors["fecha_inicio"] = "La fecha de inicio no puede ser antes que la fecha de cierre"
            datos_del_maestro["form"] = formulario
            return render(request, 'foros/registro-foro/RegistroForo.html', datos_del_maestro)
    raise Http404


@login_required()
def editar_foro(request, codigo_clase, id_foro):
    """
    Muestra la plantila para editar la informacion de un foro de una clase
    :param request: La solcitud del usuario
    :param codigo_clase: El codigo de la clase en donde se encuentra registrado el foro
    :param id_foro: El id del foro a editar
    :return: un render o un redirect
    """
    if request.user.es_maestro:
        datos_del_maestro = {}
        datos_del_maestro["clase_actual"] = request.user.persona.maestro.clase_set.filter(codigo=codigo_clase).first()
        if request.method == "GET":
            if datos_del_maestro["clase_actual"] is not None:
                if _validar_existe_foro_maestro(request.user.persona.maestro, codigo_clase, id_foro):
                    foro_actual = Foro.objects.filter(pk=id_foro).first()
                    datos_del_maestro["form"] = _crear_formulario_con_informacion_de_foro(foro_actual)
                    return render(request, 'foros/editar-foro/EditarForo.html', datos_del_maestro)
            return render(request, 'generales/NoEncontrada.html', datos_del_maestro)
        elif request.method == "POST":
            if datos_del_maestro["clase_actual"] is not None:
                if _validar_existe_foro_maestro(request.user.persona.maestro, codigo_clase, id_foro):
                    formulario = ForoForm(request.POST)
                    if formulario.is_valid():
                        datos = formulario.cleaned_data
                        if validar_fecha_cierre_mayor_a_fecha_apertura(datos["fecha_inicio"], datos["fecha_cierre"]):
                            _actualizar_informacion_foro(id_foro, datos["nombre"], datos["descripcion"],
                                                              datos["fecha_inicio"], datos["fecha_cierre"])
                            return redirect('consultar_foro', codigo_clase=codigo_clase,
                                            id_foro=id_foro)
                        else:
                            formulario.errors["fecha_inicio"] = "La fecha de inicio no puede ser antes que la fecha " \
                                                                "de cierre"
                    datos_del_maestro["form"] = formulario
                    return render(request, 'foros/editar-foro/EditarForo.html', datos_del_maestro)
        raise Http404
    else:
        return redirect('inicio')


def _crear_formulario_con_informacion_de_foro(foro):
    """
    Crea un formulario y le coloca en los campos la información de un Foro
    :param foro: El foro del cual se podra la información en sus campos
    :return: Un ForoForm
    """
    formulario = ForoForm()
    formulario.fields["nombre"].initial = foro.nombre
    formulario.fields["descripcion"].initial = foro.descripcion
    formulario.fields["fecha_inicio"].initial = foro.fecha_de_inicio
    formulario.fields["fecha_cierre"].initial = foro.fecha_de_cierre
    return formulario


def _actualizar_informacion_foro(id_foro, nombre, descripcion, fecha_inicio, fecha_cierre):
    """
    Actualiza la información del foro con el id_foro
    :param id_foro: El id del foro a actualizar la información
    :param nombre: El nuevo nombre del foro
    :param descripcion: La nueva descripción del foro
    :param fecha_inicio: La nueva fecha de inicio del foro
    :param fecha_cierre: La nueva fecha de cierre del foro
    :return: None
    """
    Foro.objects.filter(pk=id_foro).update(nombre=nombre, descripcion=descripcion, fecha_de_inicio=fecha_inicio,
                                           fecha_de_cierre=fecha_cierre)


def _registrar_foro(id_clase, nombre, descripcion, fecha_inicio, fecha_cierre):
    """
    Rigistra un nuevo for en la clase con el id_clase
    :param id_clase: El id de la clase en donde se registrara el foro
    :param nombre: El nombre que tendra el foro
    :param descripcion: La descripcion del foro
    :param fecha_inicio: La fecha de inicio del foro
    :param fecha_cierre: La fecha de cierre del foro
    :return: None
    """
    foro = Foro(clase_id=id_clase, nombre=nombre, descripcion=descripcion, fecha_de_inicio=fecha_inicio,
                fecha_de_cierre=fecha_cierre)
    foro.save()


@login_required()
def consultar_foro(request, codigo_clase, id_foro):
    """
    Muestra la informacion de un foro con sus participaciones y respuestas
    :param request: La solicitud del usuario
    :param codigo_clase: El codigo de la clase en donde pertenece el foro a consultar
    :param id_foro: El id del foro a mostrar
    :return: Un render
    """
    if request.method == "GET":
        if request.user.es_maestro:
            datos_del_maestro = {}
            datos_del_maestro["clase_actual"] = request.user.persona.maestro.clase_set.filter(
                codigo=codigo_clase).first()
            if datos_del_maestro["clase_actual"] is not None:
                datos_del_maestro["foro"] = datos_del_maestro["clase_actual"].foro_set.filter(pk=id_foro).first()
                if datos_del_maestro["foro"] is not None:
                    _actualizar_estado_foro(datos_del_maestro["foro"])
                    datos_del_maestro["participaciones"] = datos_del_maestro["foro"].participacion_set. \
                        filter(eliminada=False).all()
                    _colocar_respuetas_de_participaciones(datos_del_maestro["participaciones"])
                    return render(request, 'foros/consultar-foro/ConsultarForo.html', datos_del_maestro)
            return render(request, 'generales/NoEncontrada.html', datos_del_maestro)
        else:
            alumno = request.user.persona.alumno
            datos_del_alumno = {}
            clase = Clase.objects.filter(codigo=codigo_clase).first()
            if clase is not None:
                inscripcion = request.user.persona.alumno.inscripcion_set. \
                    filter(aceptado='Aceptado', clase_id=clase.pk).first()
                if inscripcion is not None:
                    datos_del_alumno["clase_actual"] = inscripcion.clase
                    datos_del_alumno["foro"] = datos_del_alumno["clase_actual"].foro_set.filter(pk=id_foro).first()
                    if datos_del_alumno["foro"] is not None:
                        _actualizar_estado_foro(datos_del_alumno["foro"])
                        datos_del_alumno["participaciones"] = datos_del_alumno["foro"].participacion_set. \
                            filter(eliminada=False).all()
                        _colocar_respuetas_de_participaciones(datos_del_alumno["participaciones"])
                        return render(request, 'foros/consultar-foro/ConsultarForo.html', datos_del_alumno)
            return render(request, 'generales/NoEncontrada.html', datos_del_alumno)
    raise Http404


def _colocar_respuetas_de_participaciones(participaciones):
    """
    Cola en las participaciones sus respuestas
    :param participaciones: Las participaciones en donde se colocaran las respuestas
    :return: None
    """
    for participacion in participaciones:
        participacion.respuestas = participacion.respuesta_set.filter(eliminada=False).all()


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
                    return redirect('consultar_foro', codigo_clase=codigo_clase, id_foro=id_foro)
        else:
            if _validar_existe_foro_alumno(request.user.persona.alumno, codigo_clase, id_foro):
                if request.POST['participacion'] is not None and request.POST['participacion'] != '':
                    _registrar_participacion(request.user.persona.pk, id_foro, request.POST['participacion'])
                    return redirect('consultar_foro', codigo_clase=codigo_clase, id_foro=id_foro)
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
                    return redirect('consultar_foro', codigo_clase=codigo_clase, id_foro=id_foro)
        else:
            if _validar_existe_participacion_foro_alumno(request.user.persona.alumno, codigo_clase, id_foro,
                                                         id_participacion):
                if request.POST['respuesta'] is not None and request.POST['respuesta'] != '':
                    _registrar_respuesta(request.user.persona.pk, id_participacion, request.POST['respuesta'])
                    return redirect('consultar_foro', codigo_clase=codigo_clase, id_foro=id_foro)
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
