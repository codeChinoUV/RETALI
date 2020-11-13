from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from apps.usuarios.models import Persona


def iniciarSesion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('paginaInicio')
        else:
            messages.error(request, 'El correo electronico o la contraseña son incorrectos')
            return redirect('login')
    else:
        if request.user.is_authenticated:
            return redirect('paginaInicio')
        else:
            return render(request, 'Login.html')


@login_required
def paginaInicio(request):
    if request.user.es_maestro:
        return render(request, 'PaginaInicioMaestro.html')
    else:
        return render(request, 'PaginaInicioAlumno.html')


def cerrarSesion(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('login')


def registro(request):
    if request.method == 'GET':
        return render(request, 'RegistroUsuario.html')
