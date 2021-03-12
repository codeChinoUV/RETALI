from django.http import Http404

from apps.clases.models import Alumno, Clase


def informacion_clases(request):
    """
    Colca la información de las clases de un alumno o maestro accesible a todas las plantillas
    :param request: La solicitud del usuario
    :return: Un diccionario
    """
    informacion_de_clases = {}
    if request.user.is_authenticated:
        if request.user.es_maestro:
            informacion_de_clases['clases'] = request.user.persona.maestro.obtener_clases_activas()
            informacion_de_clases['cantidad_de_clases'] = len(informacion_de_clases['clases'])
        else:
            alumno = Alumno.objects.filter(pk=request.user.persona.pk).first()
            informacion_de_clases['clases'] = alumno.obtener_clases_inscrito()
            informacion_de_clases['cantidad_clases'] = len(informacion_de_clases['clases'])
            informacion_de_clases['cantidad_clases_aceptado'] = alumno.obtener_cantidad_de_clases_aceptado()
            informacion_de_clases['cantidad_clases_rechazado'] = alumno.obtener_cantidad_de_clases_rechazado()
            informacion_de_clases['cantidad_clases_en_espera'] = alumno.obtener_cantidad_de_clases_en_espera()
    return informacion_de_clases


def colocar_clase_actual(request):
    """
    Colaca la información de la clase actaul disponible para todas las plantillas
    :param request: La solicitud del usuario
    :return: un diccionario
    """
    clase_actual_processor = {}
    if 'codigo_clase' in request.resolver_match.kwargs.keys():
        codigo_clase = request.resolver_match.kwargs['codigo_clase']
        if request.user.es_maestro:
            clase_actual = request.user.persona.maestro.clase_set.filter(codigo=codigo_clase, abierta=True).first()
            if clase_actual is not None:
                clase_actual_processor['clase_actual'] = clase_actual
            else:
                raise Http404
        else:
            clase_actual = request.user.alumno.inscripcion_set.filer(clase__codigo=codigo_clase, aceptado='Aceptado'). \
                select_related('clase')
            if clase_actual is not None:
                clase_actual_processor['clase_actual'] = clase_actual.clase
            else:
                raise Http404
    return clase_actual_processor

