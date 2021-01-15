import datetime

import pytz
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect

from apps.foros.forms import ForoForm
from apps.foros.models import Foro
from apps.usuarios.views import obtener_informacion_de_clases_de_maestro


@login_required
def consultar_foros_maestro(request, codigo_clase):
    if request.method == "GET":
        if request.user.es_maestro:
            datos_del_maestro = obtener_informacion_de_clases_de_maestro(request.user.persona.maestro)
            datos_del_maestro["clase_actual"] = request.user.persona.maestro.clase_set.filter(
                codigo=codigo_clase).first()
            if datos_del_maestro["clase_actual"] is not None:
                datos_del_maestro["foros"] = datos_del_maestro["clase_actual"].foro_set.filter(eliminado=False).all().\
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
