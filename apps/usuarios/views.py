from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from apps.clases.models import Inscripcion, Alumno, Maestro
import re
from apps.foros.models import Foro


def redireccion_path_vacio(request):
    """
    Redigere al usuario a la pagina principal o la pagina de inicio de sesion
    :param request: La solicitud del cliente
    :return: Redirect a la pagina indicada
    """
    if request.user.is_authenticated:
        return redirect('paginaInicio')
    else:
        return redirect('login')


def iniciar_sesion(request):
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
def pagina_inicio(request):
    """
    Renderiza la pagina de inicio del maestro o del alumno
    :param request: La solictud del cliente
    :return: Un render de la pagina adecuada
    """
    if request.user.es_maestro:
        datos = obtener_informacion_de_clases_de_maestro(request.user.persona.maestro)
        return render(request, 'usuarios/paginaInicio/PaginaInicioMaestro.html', datos)
    else:
        # from apps.clases.views import unir_alumnos_a_clase
        # unir_alumnos_a_clase(codigo_clase='phrdyqmxhj', id_alumno=request.user.persona.alumno.pk)
        datos_de_las_clases_del_alumno = {}
        return render(request, 'PaginaInicioAlumno.html', datos_de_las_clases_del_alumno)


def obtener_informacion_de_clases_de_maestro(maestro):
    """
    Recupera la información de las clases del maestro
    :param maestro: El maestro del cual se recuperaran las clases
    :return: Un diccionario con las clases y la cantidad de clases
    """
    datos = {
        'cantidad_clases' : 0,
        'clases': None
    }
    if maestro.clase_set.exists():
        datos = {
            'clases': maestro.clase_set.filter(abierta=True),
            'cantidad_clases': maestro.clase_set.filter(abierta=True).count()
        }
    return datos


def obtener_informacion_de_clases_del_alumno(alumno):
    """
    Recuoera la información de las clases del alumno
    :param alumno: El alumno a recuperar sus clases
    :return: Un diccionario con las clases del alumno en las que se encuentra inscrito y la cantidad de clases
    """
    if alumno.inscripcion_set.exists():
        clases = []
        for inscripcion in alumno.inscripcion_set.all():
            clases.append(inscripcion.clase)
        datos = {
            'clases': clases,
            'cantidad_clases': len(clases)
        }
        return datos


def cerrar_sesion(request):
    """
    Cierra la sesion del usuario actual
    :param request: La solicitud
    :return: Redirect hacia el login
    """
    if request.user.is_authenticated:
        logout(request)
    return redirect('login')


def registrar_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('correoElectronico')
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirmarContraseña')
        nombre = request.POST.get('nombre')
        apellidos = request.POST.get('apellidos')
        telefono = request.POST.get('telefono')
        tipoUsuario = request.POST.get('tipoUsuario')
        es_maestro = validar_tipo_usuario(tipoUsuario)
        if validar_campos_no_vacios(username, password, nombre, apellidos, telefono):
            if es_correo_valido(username):
                if validar_contrasena(password, confirmPassword):
                    Usuario = get_user_model()
                    user = Usuario.objects.create_user(email=username, password=password, es_maestro=es_maestro)
                    crear_tipo_usuario(nombre, apellidos, telefono, user, es_maestro)
                    return redirect('login')
                else:
                    messages.error(request, 'Las contraseñas no coinciden')
                    return redirect('registro')
            else:
                messages.error(request, 'El correo ingresado es inválido')
                return redirect('registro')
        else:
            messages.error(request, 'Favor de ingresar información en todos los campos')
            return redirect('registro')
    return render(request, 'RegistroUsuario.html')


def validar_contrasena(password, confirmPassword):
    if password == confirmPassword:
        return True
    else:
        return False


def validar_tipo_usuario(tipoUsuario):
    if tipoUsuario == 'Maestro':
        return True
    else:
        return False


def crear_tipo_usuario(nombre, apellidos, telefono, user, esMaestro):
    if esMaestro:
        maestro = Maestro(nombre=nombre, apellidos=apellidos, numero_telefonico=telefono, foto_de_perfil="",
                          usuario=user)
        maestro.save()
    else:
        alumno = Alumno(nombre=nombre, apellidos=apellidos, numero_telefonico=telefono, foto_de_perfil="",
                        usuario=user)
        alumno.save()


def es_correo_valido(correo):
    if re.match('^[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}$', correo):
        return True
    else:
        return False


def validar_campos_no_vacios(username, password, nombre, apellidos, telefono):
    if not username:
        return False
    elif not password:
        return False
    elif not nombre:
        return False
    elif not apellidos:
        return False
    elif not telefono:
        return False
    else:
        return True

def validar_correo_no_registrado(correo):

    return True

    return False