import datetime

import pytz
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render

from apps.foros.models import Foro
from apps.usuarios.views import obtener_informacion_de_clases_de_maestro


@login_required
def consultar_foros_maestro(request, codigo_clase):
    if request.method == "GET":
        if request.user.es_maestro:
            datos_del_maestro = obtener_informacion_de_clases_de_maestro(request.user.persona.maestro)
            datos_del_maestro["clase_actual"] = request.user.persona.maestro.clase_set.filter(codigo=codigo_clase).first()
            if datos_del_maestro["clase_actual"] is not None:
                datos_del_maestro["foros"] = datos_del_maestro["clase_actual"].foro_set.filter(eliminado=False).all()
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
