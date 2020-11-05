from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout


# Create your views here.

def iniciarSesion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('paginaInicio')
    else:
        if request.user.is_authenticated:
            return redirect('paginaInicio')
        else:
            return render(request, 'Login.html')


def paginaInicio(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        return render(request, 'PaginaInicio.html')


def cerrarSesion(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('login')
