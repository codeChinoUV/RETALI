from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from apps.actividades.forms import ActividadForm
from apps.actividades.models import Actividad
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
        datos_del_maestro = obtener_informacion_de_clases_de_maestro(request.user.persona.maestro)
        datos_del_maestro['clase_actual'] = request.user.persona.maestro.clase_set.filter(abierta=True,
                                                                                          codigo=codigo_clase).first()
        if datos_del_maestro['clase_actual'] is not None:
            datos_del_maestro['actividades'] = datos_del_maestro['clase_actual'].actividad_set.all()
            return render(request, 'actividades/consultar-actividades-maestro/ConsultarActividadesMaestro.html',
                          datos_del_maestro)


@login_required()
def registrar_actividad(request, codigo_clase):
    if not request.user.es_maestro:
        return redirect('paginaInicio')
    else:
        datos_del_maestro = obtener_informacion_de_clases_de_maestro(request.user.persona.maestro)
        clase_actual = request.user.persona.maestro.clase_set.filter(abierta=True, codigo=codigo_clase).first()
        if clase_actual is not None:
            datos_del_maestro['form'] = ActividadForm()
            if request.method == "POST":
                formulario = ActividadForm(request.POST)
                if formulario.is_valid():
                    datos_de_la_actividad = formulario.cleaned_data
                    actividad = Actividad(nombre=datos_de_la_actividad['nombre'],
                                          descripcion=datos_de_la_actividad['descripcion'],
                                          fecha_de_inicio=datos_de_la_actividad['fecha_inicio'],
                                          fecha_de_cierre=datos_de_la_actividad['fecha_cierre'],
                                          clase_id=clase_actual.id)
                    actividad.save()
                    return redirect('actividades', codigo_clase=codigo_clase)
                else:
                    datos_del_maestro['form'] = formulario
                    return render(request, 'actividades/registrar-actividad/RegistrarActividad.html', datos_del_maestro)
            else:
                return render(request, 'actividades/registrar-actividad/RegistrarActividad.html', datos_del_maestro)
        else:
            return render(request, 'generales/NoEncontrada.html', datos_del_maestro)
