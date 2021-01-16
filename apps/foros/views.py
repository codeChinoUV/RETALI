import datetime

import pytz
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect

from apps.clases.models import Clase
from apps.foros.forms import ForoForm
from apps.foros.models import Foro, Participacion, Respuesta
from apps.usuarios.views import obtener_informacion_de_clases_de_maestro, obtener_informacion_de_clases_del_alumno


@login_required
def consultar_foros_maestro(request, codigo_clase):
    if request.method == "GET":
        if request.user.es_maestro:
            datos_del_maestro = obtener_informacion_de_clases_de_maestro(request.user.persona.maestro)
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
    now = datetime.datetime.today()
    now = pytz.utc.localize(now)
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
        if foro.estado == 'Abierto':
            cantidad_abiertos += 1
    return cantidad_abiertos


@login_required()
def registrar_foro(request, codigo_clase):
    if request.user.es_maestro:
        datos_del_maestro = obtener_informacion_de_clases_de_maestro(request.user.persona.maestro)
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
                _registrar_foro(datos_del_maestro["clase_actual"].pk, foro["nombre"], foro["descripcion"],
                                foro["fecha_inicio"], foro["fecha_cierre"])
                return redirect('foros', codigo_clase=codigo_clase)
            else:
                datos_del_maestro["form"] = formulario
                return render(request, 'foros/registro-foro/RegistroForo.html', datos_del_maestro)
    raise Http404


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
    if request.user.es_maestro:
        datos_del_maestro = obtener_informacion_de_clases_de_maestro(request.user.persona.maestro)
        datos_del_maestro["clase_actual"] = request.user.persona.maestro.clase_set.filter(
            codigo=codigo_clase).first()
        if datos_del_maestro["clase_actual"] is not None:
            datos_del_maestro["foro"] = datos_del_maestro["clase_actual"].foro_set.filter(pk=id_foro).first()
            if datos_del_maestro["foro"] is not None:
                datos_del_maestro["participaciones"] = datos_del_maestro["foro"].participacion_set. \
                    filter(eliminada=False).all()
                _colocar_respuetas_de_participaciones(datos_del_maestro["participaciones"])
                return render(request, 'foros/consultar-foro/ConsultarForo.html', datos_del_maestro)
        return render(request, 'generales/NoEncontrada.html', datos_del_maestro)
    else:
        datos_del_alumno = obtener_informacion_de_clases_del_alumno(request.user.persona.alumno)
        clase = Clase.objects.filter(codigo=codigo_clase).first()
        if clase is not None:
            inscripcion = request.user.persona.alumno.inscripcion_set. \
                filter(aceptado='Aceptado', clase_id=clase.pk).first()
            if inscripcion is not None:
                datos_del_alumno["clase_actual"] = inscripcion.clase
                datos_del_alumno["foro"] = datos_del_alumno["clase_actual"].foto_set.filter(pk=id_foro).first()
                if datos_del_alumno["foro"] is not None:
                    datos_del_alumno["participaciones"] = datos_del_alumno["foro"].participacion_set. \
                        filter(eliminada=False).all()
                    _colocar_respuetas_de_participaciones(datos_del_alumno["participaciones"])
                    return render(request, 'foros/consultar-foro/ConsultarForo.html', datos_del_alumno)
        return render(request, 'generales/NoEncontrada.html', datos_del_alumno)


def _colocar_respuetas_de_participaciones(participaciones):
    for participacion in participaciones:
        participacion.respuestas =participacion.respuesta_set.filter(eliminada=False).all()

@login_required()
def participar_en_foro(request, codigo_clase, id_foro):
    if request.method == "POST":
        if request.user.es_maestro:
            if _validar_existe_foro_maestro(request.user.persona.maestro, codigo_clase, id_foro):
                if request.POST['participacion'] is not None and request.POST['participacion'] != '':
                    _registrar_participacion(request.user.persona.pk, id_foro, request.POST['participacion'])
                    return redirect('consultar_foro', codigo_clase=codigo_clase, id_foro=id_foro)
        else:
            if _validar_existe_foro_alumno(request.user.persona.alumno, codigo_clase, id_foro):
                if request.POST['participacion'] is not None and request.POST['particioacion'] != '':
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
        inscripcion = alumno.inscripcion_set(aceptado='Aceptado', clase_id=clase.pk).first()
        if inscripcion is not None:
            foro = inscripcion.clase.foro_set.filter(pk=id_foro).first()
            if foro is not None:
                existe_foro = True
    return existe_foro


@login_required()
def responder_participacion(request, codigo_clase, id_foro, id_participacion):
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
    respuesta_anteriores = Respuesta.objects.filter(participacion_id=id_participacion).count()
    respuesta_actual = respuesta_anteriores + 1
    respuesta = Respuesta(autor_id=id_persona, participacion_id=id_participacion, respuesta=respuesta,
                          numero_respuesta=respuesta_actual)
    respuesta.save()
