from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .forms import ClaseForm


@login_required
def registrar_clase(request):
    if request.method == 'GET':
        form = ClaseForm()
        return render(request, 'RegistroClase.html', {'form': form})
    elif request.method == "POST":
        form = ClaseForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            datos = form.cleaned_data
            print(datos.keys())
            print("Hoooola")
        return render(request, 'RegistroClase.html', {'form': form})
