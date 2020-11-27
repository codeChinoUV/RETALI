import random

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ClaseForm
from .models import Clase


@login_required
def registrar_clase(request):
    """
    Maneja las peticiones realizadas a la ruta 'registro_maestro/
    :param request: Contiene la información de la petición
    :return: Un redirect a la pagina adecuada o un render de un Template
    """
    if not request.user.es_maestro:
        return redirect('paginaInicio')
    if request.method == 'GET':
        form = ClaseForm()
        return render(request, 'clases/registro-clase/RegistroClase.html', {'form': form})
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
            return render(request, 'clases/registro-clase/RegistroClase.html', {'form': form})


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
