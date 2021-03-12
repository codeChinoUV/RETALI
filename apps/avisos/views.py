from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect

from apps.avisos.forms import AvisoForm
from apps.avisos.models import Aviso
from apps.clases.models import Clase


@login_required()
def consultar_avisos(request, codigo_clase):
    """
    Muestra la informacion de los avisos realizados en una clase
    :param request: La solicitud del cliente
    :param codigo_clase: El codigo de la clase a consultar sus avisos
    :return: Un render
    """
    if request.method == "GET":
        if request.user.es_maestro:
            datos_del_maestro = {}
            if _validar_existe_clase(request.user.persona.maestro, codigo_clase):
                datos_del_maestro["clase_actual"] = Clase.objects.filter(codigo=codigo_clase).first()
                datos_del_maestro["avisos"] = datos_del_maestro["clase_actual"].aviso_set.all() \
                    .order_by('-fecha_publicado')
                return render(request, 'avisos/consultar-avisos/ConsultarAvisos.html', datos_del_maestro)
            return render(request, 'generales/NoEncontrada.html', datos_del_maestro)
        else:
            datos_del_alumno = {}
            if _validar_existe_clase_alumno(request.user.persona.alumno, codigo_clase):
                datos_del_alumno["clase_actual"] = Clase.objects.filter(codigo=codigo_clase).first()
                datos_del_alumno["avisos"] = datos_del_alumno["clase_actual"].aviso_set.all() \
                    .order_by('-fecha_publicado')
                return render(request, 'avisos/consultar-avisos-alumno/ConsultarAvisosAlumno.html', datos_del_alumno)
            return render(request, 'generales/NoEncontrada.html', datos_del_alumno)
    raise Http404


def _validar_existe_clase(maestro, codigo_clase):
    """
    Valida que exista una clase del alumno
    :param maestro: El maestro de a validr que la clase tenga la clase con el codigo
    :param codigo_clase: El codigo de la clase a validar si existe
    :return: True si la clase existe o False si no
    """
    existe_la_clase = False
    clase = Clase.objects.filter(codigo=codigo_clase).first()
    if clase is not None:
        if maestro.clase_set.filter(abierta=True, pk=clase.pk).count() > 0:
            existe_la_clase = True
    return existe_la_clase


def _validar_existe_clase_alumno(alumno, codigo_clase):
    """
    Valida que exista una clase del alumno
    :param alumno: El alumno a validar que tenga la clase inscrito
    :param codigo_clase: El codigo de la clase a validar si existe
    :return: True si la clase existe o False si no
    """
    existe_la_clase = False
    clase = Clase.objects.filter(codigo=codigo_clase).first()
    if clase is not None:
        inscripcion = alumno.inscripcion_set.filter(aceptado='Aceptado', clase_id=clase.pk).first()
        if inscripcion is not None:
            existe_la_clase = True
    return existe_la_clase


@login_required()
def crear_aviso(request, codigo_clase):
    """
    Muestra la plantilla para crear un nuevo aviso
    :param request: La solicitud del cliente
    :param codigo_clase: El codigo de la clase en donde se registrara el aviso
    :return: un rendero un redirect
    """
    if request.user.es_maestro:
        datos_del_maestro = {}
        if request.method == "GET":
            if _validar_existe_clase(request.user.persona.maestro, codigo_clase):
                datos_del_maestro["clase_actual"] = Clase.objects.filter(abierta=True, codigo=codigo_clase).first()
                datos_del_maestro["form"] = AvisoForm()
                return render(request, 'avisos/registrar-aviso/RegistrarAviso.html', datos_del_maestro)
            return render(request, 'generales/NoEncontrada.html', datos_del_maestro)
        elif request.method == "POST":
            if _validar_existe_clase(request.user.persona.maestro, codigo_clase):
                formulario = AvisoForm(request.POST)
                if formulario.is_valid():
                    formulario_valido = formulario.cleaned_data
                    _registrar_aviso(codigo_clase, formulario_valido["nombre"], formulario_valido["descripcion"])
                    return redirect('avisos', codigo_clase=codigo_clase)
                datos_del_maestro["clase_actual"] = Clase.objects.filter(abierta=True, codigo=codigo_clase).first()
                datos_del_maestro["form"] = formulario
                return render(request, 'avisos/registrar-aviso/RegistrarAviso.html', datos_del_maestro)
    return redirect('inicio')


def _registrar_aviso(codigo_clase, nombre, descripcion):
    """
    Registra un nuevo aviso en la clase con el codgio clase
    :param codigo_clase: El codigo de la clase en donde se registrara el aviso
    :param nombre: El nombre del aviso
    :param descripcion: La descripcion del aviso
    :return: None
    """
    clase = Clase.objects.filter(codigo=codigo_clase).first()
    aviso = Aviso(clase_id=clase.pk, nombre=nombre, descripcion=descripcion)
    aviso.save()
