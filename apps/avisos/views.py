from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from apps.avisos.forms import AvisoForm
from apps.avisos.models import Aviso
from apps.clases.models import Clase
from apps.usuarios.views import obtener_informacion_de_clases_de_maestro


@login_required()
def consultar_avisos(request, codigo_clase):
    if request.method == "GET":
        if request.user.es_maestro:
            datos_del_maestro = obtener_informacion_de_clases_de_maestro(request.user.persona.maestro)
            if _validar_existe_clase(request.user.persona.maestro, codigo_clase):
                datos_del_maestro["clase_actual"] = Clase.objects.filter(codigo=codigo_clase).first()
                datos_del_maestro["avisos"] = datos_del_maestro["clase_actual"].aviso_set.all()
                return render(request, 'avisos/consultar-avisos/ConsultarAvisos.html', datos_del_maestro)
            return render(request, 'generales/NoEncontrada.html', datos_del_maestro)


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


@login_required()
def crear_aviso(request, codigo_clase):
    if request.user.es_maestro:
        datos_del_maestro = obtener_informacion_de_clases_de_maestro(request.user.persona.maestro)
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
    return redirect('paginaInicio')


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
