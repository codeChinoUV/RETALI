import random

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ClaseForm
from .models import Clase


@login_required
def registrar_clase(request):
    if not request.user.es_maestro:
        return redirect('paginaInicio')
    if request.method == 'GET':
        form = ClaseForm()
        return render(request, 'RegistroClase.html', {'form': form})
    elif request.method == "POST":
        form = ClaseForm(request.POST, request.FILES)
        if form.is_valid():
            datos = form.cleaned_data
            while True:
                codigo_generado = _generar_codigo_alfebetico()
                cantidad_de_clases_con_el_mismo_codigo = Clase.objects.filter(codigo=codigo_generado).count()
                if cantidad_de_clases_con_el_mismo_codigo == 0:
                    break
            clase = Clase(nombre=datos['nombre'], abierta=True, escuela=datos['escuela'],
                          maestro=request.user.persona.maestro, codigo=codigo_generado)
            clase.save()
            return redirect('paginaInicio')
        else:
            return render(request, 'RegistroClase.html', {'form': form})


def _generar_codigo_alfebetico():
    frase = ""
    lista = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    for i in range(0, 10):
        p = lista[random.randint(0, 25)]
        frase += p
    return frase
