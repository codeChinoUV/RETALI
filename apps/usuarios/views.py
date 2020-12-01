from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from apps.clases.models import Inscripcion, Alumno, Maestro
import re

from apps.foros.models import Foro


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
    if request.user.es_maestro:
        datos = obtener_informacion_de_clases_de_maestro(request.user.persona.maestro)
        return render(request, 'usuarios/paginaInicio/PaginaInicioMaestro.html', datos)
    else:
        datos_de_las_clases_del_alumno = _obtener_informacion_de_las_clases_del_alumno(request.user.persona.alumno)
        return render(request, 'PaginaInicioAlumno.html', datos_de_las_clases_del_alumno)


def obtener_informacion_de_clases_de_maestro(maestro):
    """
    Recupera la información de las clases del maestro
    :param maestro: El maestro del cual se recuperaran las clases
    :return: Un diccionario con las clases y la cantidad de clases
    """
    datos = {
        'clases': [],
        'cantidad_clases': 0
    }
    if maestro.clase_set.exists():
        datos['clases'] = maestro.clase_set.filter(abierta=True)
        datos['cantidad_clases'] = (datos['clases'])
    return datos


def _obtener_informacion_de_las_clases_del_alumno(alumno):
    datos = {
        'clases_inscrito': 0,
        'clases_pendientes': 0,
        'foros_abiertos': 0,
        'anuncios_sin_leer': 0,
        'tareas_que_se_cierran_hoy': 0,
        'tareas_que_se_cierran_esta_semana': 0
    }
    if Inscripcion.objects.filter(alumno=alumno).exists():
        inscritos = Inscripcion.objects.get(alumno=alumno)
        for inscripcion in inscritos:
            if inscripcion.aceptado:
                datos['clases_inscrito'] += 1
                for foro in inscripcion.clase.foro_set.all():
                    if foro.EstadoForo == Foro.EstadoForo.ABIERTO:
                        datos['foros_abiertos'] += 1
                for aviso in inscripcion.clase.anuncio_set.all():
                    if alumno not in aviso.leido_por:
                        datos['anuncios_sin_leer'] += 1
                # for tarea in inscripcion.clase.actividad_set.filter(fecha_de_cierre=):
            else:
                datos['clases_pendientes'] += 1

    return datos


def cerrar_sesion(request):
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
