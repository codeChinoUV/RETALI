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
    if 'codigo_clase' in request.resolver_match.kwargs.keys():
        clase_actual = Clase.objects.filter(codigo=request.resolver_match.kwargs['codigo_clase'],
                                            abierta=True).first()
        if clase_actual is not None:
            return {'clase_actual': clase_actual}
    return {}
