import datetime

import pytz
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse

from apps.actividades.forms import ActividadForm, ActividadDisableForm
from apps.actividades.models import Actividad, Entrega, Archivo, Revision
from apps.clases.models import Clase
from apps.clases.views import obtener_cantidad_de_alumnos_inscritos_a_clase
from apps.usuarios.views import obtener_informacion_de_clases_de_maestro


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
        datos_del_maestro = obtener_informacion_de_clases_de_maestro(request.user.persona.maestro)
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
                _obtener_cantidad_de_actividades_abiertas(datos_del_maestro['actividades'])
            # _registrar_entrega(1, "adjunto el link del repositorio de github: https://github.com/codeChinoUV/RETALI.git",
            #                   2)
            return render(request, 'actividades/consultar-actividades-maestro/ConsultarActividadesMaestro.html',
                          datos_del_maestro)


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
        datos_del_maestro = obtener_informacion_de_clases_de_maestro(request.user.persona.maestro)
        datos_del_maestro['clase_actual'] = request.user.persona.maestro.clase_set. \
            filter(abierta=True, codigo=codigo_clase).first()
        if datos_del_maestro['clase_actual'] is not None:
            datos_del_maestro['form'] = ActividadForm()
            if request.method == "POST":
                formulario = ActividadForm(request.POST)
                if formulario.is_valid():
                    datos_de_la_actividad = formulario.cleaned_data
                    actividad = Actividad(nombre=datos_de_la_actividad['nombre'],
                                          descripcion=datos_de_la_actividad['descripcion'],
                                          fecha_de_inicio=datos_de_la_actividad['fecha_inicio'],
                                          fecha_de_cierre=datos_de_la_actividad['fecha_cierre'],
                                          clase_id=datos_del_maestro['clase_actual'].id)
                    actividad.save()
                    return redirect('actividades', codigo_clase=codigo_clase)
                else:
                    datos_del_maestro['form'] = formulario
                    return render(request, 'actividades/registrar-actividad/RegistrarActividad.html', datos_del_maestro)
            else:
                return render(request, 'actividades/registrar-actividad/RegistrarActividad.html', datos_del_maestro)
        else:
            return render(request, 'generales/NoEncontrada.html', datos_del_maestro)


def _actualizar_estado_actividades(actividades):
    """
    Actualiza el estado de las actividades que se le pasan, verificando si esta abierta o no
    :param actividades: Las actividades a las que se le actualizara el estado
    :return: None
    """
    if actividades is not None:
        now = datetime.datetime.today()
        now = pytz.utc.localize(now)
        for actividad in actividades:
            if actividad.fecha_de_inicio > now:
                Actividad.objects.filter(pk=actividad.pk).update(estado='Por abrir')
                actividad.estado = 'Por abrir'
            else:
                if actividad.fecha_de_cierre < now:
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


def _obtener_cantidad_de_actividades_abiertas(actividades):
    """
    Cuenta la cantidad de actividades que su fecha de entrega es despues de la fecha actual
    :param actividades: Las actividades a checar
    :return: La cantidad de actividades abiertas
    """
    now = datetime.datetime.today()
    now = pytz.utc.localize(now)
    cantidad_actividades_abiertas = 0
    for actividad in actividades:
        if actividad.fecha_de_cierre > now:
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
    if not request.user.es_maestro:
        return redirect('paginaInicio')
    else:
        datos_del_maestro = obtener_informacion_de_clases_de_maestro(request.user.persona.maestro)
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


def _registrar_entrega(actividad_id, entrega, alumno_id):
    entrega = Entrega(alumno_id=alumno_id, actvidad_id=actividad_id, comentarios=entrega)
    entrega.save()


def revisar_entrega_actividad(request, codigo_clase, id_actividad, id_entrega):
    if not request.user.es_maestro:
        return redirect('paginaInicio')
    else:
        datos_del_maestro = obtener_informacion_de_clases_de_maestro(request.user.persona.maestro)
        datos_del_maestro['clase_actual'] = request.user.persona.maestro.clase_set. \
            filter(codigo=codigo_clase, abierta=True).first()
        if _validar_existe_entrega(codigo_clase, id_actividad, id_entrega, request.user.persona.maestro):
            datos_del_maestro['actividad_actual'] = datos_del_maestro['clase_actual']. \
                actividad_set.filter(pk=id_actividad).first()
            datos_del_maestro['form'] = ActividadDisableForm()
            datos_del_maestro['entrega_actual'] = datos_del_maestro['actividad_actual']. \
                entrega_set.filter(pk=id_actividad).first()
            if datos_del_maestro['entrega_actual'].revision is not None:
                datos_del_maestro['revision'] = datos_del_maestro['entrega_actual'].revision
            if request.method == 'GET':
                return render(request, 'actividades/revisar-entrega-actividad/RevisarEntregaActividad.html',
                              datos_del_maestro)
            elif request.method == 'POST':
                hoy = datetime.datetime.today()
                hoy = pytz.utc.localize(hoy)
                actividad_actual = datos_del_maestro['clase_actual'].actividad_set.filter(pk=id_actividad).first()
                if actividad_actual.fecha_de_cierre < hoy:
                    if request.POST.get('calificacion') is None or request.POST.get('calificacion') == '':
                        datos_del_maestro['errores'] = {
                            'calificacion': 'Debe de escoger una calificacion'
                        }
                    else:
                        if datos_del_maestro['entrega_actual'].revision is not None:
                            Revision.objects.filter(id_entrega=datos_del_maestro['entrega_actual'.pk]).\
                                update(calificacion=request.POST.get('calificacion'), retroalimentacion=request.POST.
                                       get('comentarios'))
                        else:
                            revision = Revision(id_actividad=actividad_actual.pk,
                                                calificacion=request.POST.get('calificacion'),
                                                retroalimentacion=request.POST.get('comentarios'))
                            revision.save()
                        return redirect('actividades')
                else:
                    datos_del_maestro['errores'] = {
                        'fecha-cierre': 'No puede guardar su revisión hasta que la activdad se cierre'
                    }
                    return render(request, 'actividades/revisar-entrega-actividad/RevisarEntregaActividad.html',
                                  datos_del_maestro)

        else:
            return render(request, 'generales/NoEncontrada.html', datos_del_maestro)


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
    if request.user.es_maestro:
        return redirect('paginaInicio')
    else:
        clase = Clase.objects.filter(abierta=True, codigo=codigo_clase).first()
        datos_del_alumno = {
            'clase_actual': request.user.persona.alumno.inscripcion_set.filter(aceptado='Aceptado',
                                                                               clase_id=clase.pk).first().clase
        }
        datos_del_alumno['actividad_actual'] = datos_del_alumno['clase_actual'].actividad_set.filter(
            pk=id_actividad).first()
        return render(request, 'actividades/entregar-actividad-alumno/EntregarActividadAlumno.html', datos_del_alumno)

def _validar_existe_actividad_de_alumno(codigo_clase, id_actividad, alumno):
    existe_actividad = False
    clase = Clase.objects.filter(abierta=True, codigo=codigo_clase).first()
    clase_del_alumno = alumno.inscripcion_set.filter(aceptado='Aceptado', clase_id=clase.pk).first().clase
    if clase_del_alumno is not None:
        if clase_del_alumno.actividad_set.filter(pk=id_actividad).count() > 0:
            existe_actividad = True
    return existe_actividad
