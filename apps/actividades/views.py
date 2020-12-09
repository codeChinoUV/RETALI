from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from apps.actividades.forms import ActividadForm
from apps.usuarios.views import obtener_informacion_de_clases_de_maestro


@login_required
def consultar_actividades_de_clase(request, codigo_clase):
    """
    Obtiene las actividades de una clase
    :param request: El request del cliente
    :param codigo_clase: El codigo de la clase de la cual se quiere obtener las actividades
    :return: Una template con sus datos o un redirect a la pagina correcta
    """
    if not request.user.es_maestro:
        return redirect('paginaInicio')
    else:
        clases = obtener_informacion_de_clases_de_maestro(request.user.persona.maestro)
        clase_actual = None
        for clase in clases['clases']:
            if clase.codigo == codigo_clase:
                clase_actual = clase
                break
        if clase_actual is not None:
            clases['actividades'] = clase_actual.actividades_set.all()
            return render(request, '')


@login_required()
def registrar_actividad(request, codigo_clase):
    if not request.user.es_maestro:
        return redirect('paginaInicio')
    else:
        datos_del_maestro = obtener_informacion_de_clases_de_maestro(request.user.persona.maestro)
        clase_actual = request.user.persona.maestro.clase_set.filter(abierta=True, codigo=codigo_clase).first()
        if clase_actual is not None:
            datos_del_maestro['form'] = ActividadForm()
            return render(request, 'actividades/registrar-actividad/RegistrarActividad.html', datos_del_maestro)
        else:
            return render(request, 'generales/NoEncontrada.html', datos_del_maestro)
