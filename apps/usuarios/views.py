from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages

from apps.clases.models import Inscripcion, Foro, Alumno, Maestro


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
            # User = get_user_model()
            # user = User.objects.create_user(email="maestro@gmail.com", password="hola9011", es_maestro=True)
            # maestro = Maestro(nombre="Jose Miguel", apellidos="Quiroz Benitez", numero_telefonico="2821125536", usuario=user)
            # maestro.save()
            return render(request, 'Login.html')


@login_required
def paginaInicio(request):
    if request.user.es_maestro:
        datos = {
            'clases': None,
            'cantidad_clases': 0
        }
        if request.user.persona.maestro.clase_set.exists():
            datos['clases'] = request.user.persona.maestro.clase_set.filter(abierta=True)
            datos['cantidad_clases'] = (datos['clases'])
        return render(request, 'PaginaInicioMaestro.html', datos)
    else:
        datos_de_las_clases_del_alumno = _obtener_informacion_de_las_clases_del_alumno(request.user.persona.alumno)
        return render(request, 'PaginaInicioAlumno.html', datos_de_las_clases_del_alumno)


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


def cerrarSesion(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('login')


def paginaRegistro(request):
    if request.method == 'GET':
        return render(request, 'RegistroUsuario.html')


def registrarUsuario(request):
    if request.method == 'POST':
        username = request.POST.get('correoElectronico')
        password = request.POST.get('password')
        tipo_usuario = request.POST.get('tipoUsuario')
        if tipo_usuario == 'Maestro':
            es_maestro = True
        else:
            es_maestro = False
        Usuario = get_user_model()
        user = Usuario.objects.create_user(email=username, password=password, es_maestro=es_maestro)
        nombre = request.POST.get('nombre')
        apellidos = request.POST.get('apellidos')
        telefono = request.POST.get('telefono')
        try:
            if es_maestro:
                maestro = Maestro(nombre=nombre, apellidos=apellidos, numero_telefonico=telefono, foto_de_perfil="",
                                  usuario=user)
                maestro.save()
            else:
                alumno = Alumno(nombre=nombre, apellidos=apellidos, numero_telefonico=telefono, foto_de_perfil="",
                                usuario=user)
                alumno.save()
            return redirect('paginaInicio')
        except:
            messages.error(request, 'No se puedo guardar')

    return render(request, 'RegistroUsuario.html')
