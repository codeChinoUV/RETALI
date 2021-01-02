import random

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ClaseForm
from .models import Clase
from ..usuarios.views import obtener_informacion_de_clases_de_maestro, _obtener_informacion_de_las_clases_del_alumno


@login_required
def registrar_clase(request):
    """
    Maneja las peticiones realizadas a la ruta 'registro_clase'
    :param request: Contiene la información de la petición
    :return: Un redirect a la pagina adecuada o un render de un Template
    """
    if not request.user.es_maestro:
        return redirect('paginaInicio')
    clases_maestro = obtener_informacion_de_clases_de_maestro(request.user.persona.maestro)
    datos = {
        'clases': clases_maestro['clases'],
        'cantidad_clases': clases_maestro['cantidad_clases']
    }
    if request.method == 'GET':
        datos['form'] = ClaseForm()
        return render(request, 'clases/registro-clase/RegistroClase.html', datos)
    elif request.method == "POST":
        form = ClaseForm(request.POST, request.FILES)
        if form.is_valid():
            datos = form.cleaned_data
            codigo_generado = _obtener_codigo_unico()
            datos['foto'].name = codigo_generado + "." + datos['foto'].name.split('.')[-1]
            clase = Clase(nombre=datos['nombre'], abierta=True, escuela=datos['escuela'],
                          maestro=request.user.persona.maestro, codigo=codigo_generado, foto=datos['foto'])
            clase.save()
            return redirect('paginaInicio')
        else:
            datos['form'] = form
            return render(request, 'clases/registro-clase/RegistroClase.html', datos)


def _generar_codigo_alfebetico():
    """
    Genera un codigo aleatorio de 10 letras
    :return: Una cadena de 10 letras
    """
    frase = ""
    lista = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    for i in range(0, 10):
        p = lista[random.randint(0, 25)]
        frase += p
    return frase


def _obtener_codigo_unico():
    """
    Obtiene un codigo de 10 letras que no se encuentre registrado
    :return: Un codigo unico de 10 letras
    """
    while True:
        codigo_generado = _generar_codigo_alfebetico()
        cantidad_de_clases_con_el_mismo_codigo = Clase.objects.filter(codigo=codigo_generado).count()
        if cantidad_de_clases_con_el_mismo_codigo == 0:
            break
    return codigo_generado


@login_required()
def informacion_clase(request, codigo_clase):
    if not request.user.es_maestro:
        return redirect('login')
    else:
        maestro = request.user.persona.maestro
        clase_actual = maestro.clase_set.filter(abierta=True, codigo=codigo_clase).first()
        clases_maestro = obtener_informacion_de_clases_de_maestro(request.user.persona.maestro)
        datos = {
            'clases': clases_maestro['clases']
        }
        if clase_actual is not None:
            datos['clase_actual'] = clase_actual
            return render(request, 'clases/informacion-clase/InformacionClase.html', datos)
        else:
            return render(request, 'generales/NoEncontrada.html', datos)


def informacion_clase_alumno(request, codigo_clase):
    if not request.user.es_alumno:
        return redirect('login')
    else:
        alumno = request.user.persona.alumno
        clase_actual = alumno.clase_set.filter(abierta=True, codigo=codigo_clase).first()
        clases_alumno = _obtener_informacion_de_las_clases_del_alumno(request.user.persona.alumno)
        datos = {
            'clases': clases_alumno['clases']
        }
        if clase_actual is not None:
            datos['clase_actual'] = clase_actual
            return render(request, 'clases/informacion-clase/InformacionClaseAlumno.html', datos)
        else:
            return render(request, 'generales/NoEncontrada.html', datos)


def unirse_clase(request):

    return render(request, 'clases/unirse_clase/unirse_clase.html')


def obtener_clase_actual(codigo_clase):
    clase_actual = Clase.objects.filter(codigo_clase=codigo_clase).first()
    print(clase_actual)
    if clase_actual is not None:
        return clase_actual
    else:
        return render('generales/NoEncontrada.html')
