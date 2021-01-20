import random

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect
from .forms import ClaseForm
from .models import Clase, Inscripcion
from ..usuarios.views import obtener_informacion_de_clases_de_maestro, obtener_informacion_de_clases_del_alumno, \
    colocar_estado_inscripcion_clase, obtener_alumnos_inscritos_a_clase, contar_estados_inscripciones_de_alumnos


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
    """
    Recupera la información de la clase de un maestro
    :param request: La solicitud del cliente
    :param codigo_clase: El codigo de la clase a obtener la informacion
    :return: Un redirect o un render
    """
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
            _colocar_informacion_clase(datos, datos['clase_actual'])
            return render(request, 'clases/informacion-clase/InformacionClase.html', datos)
        else:
            return render(request, 'generales/NoEncontrada.html', datos)


def obtener_cantidad_de_alumnos_inscritos_a_clase(id_clase):
    """
    Obtiene la cantidad de alumnos inscritos a una clase
    :param id_clase: El id de la clase
    :return: La cantidad de alumnos aceptados en la clase
    """
    return Clase.objects.filter(pk=id_clase).first().inscripcion_set.filter(aceptado='Aceptado').count()


@login_required()
def obtener_informacion_clase(request, codigo_clase):
    """
    Responde a una solicitud AJAX con la información de una clase
    :param request: La solicitud del usuario
    :param codigo_clase: El codigo de la clase de la cual se devolvera la informacion
    :return: Un JSON con la informacion del maestro
    """
    if request.is_ajax and request.method == "GET":
        clase_con_codigo = Clase.objects.filter(codigo=codigo_clase, abierta=True).first()
        if clase_con_codigo is not None:
            datos = _crearJSONClase(clase_con_codigo)
            return JsonResponse(datos)
        else:
            return JsonResponse({'error': 'No exite ninguna clase con el codigo indicado'})
    raise Http404


def _crearJSONClase(clase):
    """
    Crea un Diccionario con los datos de una clase
    :param clase: La clase de la cual se creara la clase
    :return: Un diccionario con la información de la clase
    """
    url_foto_maeestro = ''
    if clase.maestro.foto_de_perfil:
        url_foto_maeestro = clase.maestro.foto_de_perfil.url
    datos_clase = {
        'nombre': clase.nombre,
        'escuela': clase.escuela,
        'foto': clase.foto.url,
        'maestro': clase.maestro.nombre + ' ' + clase.maestro.apellidos,
        'foto_maestro': url_foto_maeestro
    }
    return datos_clase


@login_required()
def unir_alumno_a_clase(request, codigo_clase):
    """
    Une un alumno a una clase al crear una inscripcion
    :param request: La solicitud del usuario
    :param codigo_clase: El codigo de la clase a la que el alumno se quiere unir
    :return: Un JSON
    """
    if not request.user.es_maestro:
        if request.is_ajax and request.method == 'GET':
            mensaje_error = _validar_inscripcion_a_clase(request.user.persona.alumno, codigo_clase)
            if mensaje_error == "":
                _registrar_inscripcion_alumno(request.user.persona.alumno.pk, codigo_clase)
                return JsonResponse({})
            else:
                return JsonResponse({'error': mensaje_error})
    raise Http404


def _registrar_inscripcion_alumno(id_alumno, codigo_clase):
    """
    Registra un alumno en una clase
    :param id_alumno: El id del alumno a inscribir en una clase
    :param codigo_clase: El codigo de la clase en la cual el alumno se va a unir
    :return: None
    """
    clase = Clase.objects.filter(codigo=codigo_clase, abierta=True).first()
    inscripcion = Inscripcion(clase_id=clase.pk, alumno_id=id_alumno)
    inscripcion.save()


def _validar_inscripcion_a_clase(alumno, codigo_clase):
    """
    Valida si existe una inscripcion previa del alumno
    :param alumno: El alumno a validar sus inscripciones
    :param codigo_clase: El codigo de la clase a validar
    :return: Un mensaje correspondiente al error
    """
    mensaje_error = "La clase a la que se desea inscribir no existe"
    clase = Clase.objects.filter(abierta=True, codigo=codigo_clase).first()
    if clase is not None:
        inscripcion = alumno.inscripcion_set.filter(clase_id=clase.pk).first()
        if inscripcion is not None:
            if inscripcion.estado == 'Aceptado':
                mensaje_error = "Ya se encuentra inscrito a esta clase"
            elif inscripcion.estado == 'Rechazado':
                mensaje_error = "El maestro de la clase rechazo su solicitud para unirse a la clase"
            else:
                mensaje_error = "El maestro aun no revisa su solicitud para unirse a la clase"
        else:
            mensaje_error = ""
    return mensaje_error


@login_required()
def informacion_clase_alumno(request, codigo_clase):
    """
    Muestra la informacion de una clase para el usuario alumno
    :param request: La solicitud del usuario
    :param codigo_clase: El codigo de la clase a mostrar la informacion
    :return: Un render o un redirect
    """
    if request.user.es_maestro:
        return redirect('login')
    else:
        alumno = request.user.persona.alumno
        clase = Clase.objects.filter(codigo=codigo_clase).first()
        inscripcion = alumno.inscripcion_set.filter(aceptado='Aceptado', clase_id=clase.id).first()
        clase_actual = inscripcion.clase
        clases_alumno = obtener_informacion_de_clases_del_alumno(request.user.persona.alumno)
        datos = {
            'clases': clases_alumno['clases']
        }
        colocar_estado_inscripcion_clase(alumno, clases_alumno['clases'])
        if clase_actual is not None:
            datos['clase_actual'] = clase_actual
            return render(request, 'clases/informacion-clase/InformacionClaseAlumno.html', datos)
        else:
            return render(request, 'generales/NoEncontrada.html', datos)


def _colocar_informacion_clase(datos, clase):
    """
    Coloca la información importante sobre las actividades, los foros y los alumnos de la clase
    :param datos: Los datos en donde se agregaran los nuevos datos sobre la clase
    :param clase: La clase de donde se obtendran los datos
    :return: None
    """
    from ..actividades.views import obtener_cantidad_total_de_actividades, obtener_cantidad_de_actividades_abiertas
    from ..foros.views import contar_foros_activos
    datos['total_de_actividades'] = obtener_cantidad_total_de_actividades(clase)
    datos['actividades_abiertas'] = obtener_cantidad_de_actividades_abiertas(clase.actividad_set.all())
    datos['total_de_foros'] = len(datos['clase_actual'].foro_set.all())
    datos['foros_abiertos'] = contar_foros_activos(datos['clase_actual'].foro_set.all())
    alumnos_de_la_clase = obtener_alumnos_inscritos_a_clase(clase)
    datos_cantidad_alumnos = {}
    contar_estados_inscripciones_de_alumnos(alumnos_de_la_clase, datos_cantidad_alumnos)
    datos['alumnos_aceptados'] = datos_cantidad_alumnos['cantidad_alumnos_aceptados']
    datos['alumnos_en_espera'] = datos_cantidad_alumnos['cantidad_alumnos_en_espera']
