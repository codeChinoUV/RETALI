import random

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.usuarios.models import Persona


class Maestro(Persona):
    """
    Representa al usuario Maestro
    """

    def obtener_clases_activas(self):
        return self.clase_set.filter(abierta=True).order_by('creada_en')


class Clase(models.Model):
    """
    Contiene la información de la clase, asi como el codigo para unirse a la clase
    """
    codigo = models.CharField(max_length=10, db_index=True)
    escuela = models.CharField(max_length=50, null=False)
    nombre = models.CharField(max_length=70, null=False)
    abierta = models.BooleanField(default=True)
    foto = models.ImageField(upload_to='clases')
    maestro = models.ForeignKey(Maestro, on_delete=models.RESTRICT)
    creada_en = models.DateField(default=timezone.now)

    def modificar_estado_inscripcion_alumno(self, id_alumno, nuevo_estado):
        self.inscripcion_set.filter(alumno_id=id_alumno).update(aceptado=nuevo_estado)

    @classmethod
    def obtener_codigo_unico(cls):
        """
        Obtiene un codigo de 10 letras que no se encuentre registrado
        :return: Un codigo unico de 10 letras
        """
        while True:
            codigo_generado = Clase._generar_codigo_alfebetico()
            cantidad_de_clases_con_el_mismo_codigo = Clase.objects.filter(codigo=codigo_generado).count()
            if cantidad_de_clases_con_el_mismo_codigo == 0:
                break
        return codigo_generado

    @classmethod
    def _generar_codigo_alfebetico(cls):
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


class Alumno(Persona):
    """
    Representa un alumno en el sistema
    """
    inscripciones = models.ManyToManyField(Clase, through='Inscripcion')

    def obtener_clases_inscrito(self):
        clases = []
        for inscripcion in self.inscripcion_set.all():
            clase = inscripcion.clase
            if clase.abierta:
                clase.estado_inscipcion = inscripcion.aceptado
                clases.append(inscripcion.clase)
        return clases

    def obtener_cantidad_de_clases_aceptado(self):
        clases = self.obtener_clases_inscrito()
        cantidad_de_clases_aceptadas = 0
        for clase in clases:
            if clase.estado_inscipcion == 'Aceptado' and clase.abierta:
                cantidad_de_clases_aceptadas += 1
        return cantidad_de_clases_aceptadas

    def obtener_cantidad_de_clases_en_espera(self):
        clases = self.obtener_clases_inscrito()
        cantidad_de_clases_en_espera = 0
        for clase in clases:
            if clase.estado_inscipcion == 'En espera' and clase.abierta:
                cantidad_de_clases_en_espera += 1
        return cantidad_de_clases_en_espera

    def obtener_cantidad_de_clases_rechazado(self):
        clases = self.obtener_clases_inscrito()
        cantidad_de_clases_rechazado = 0
        for clase in clases:
            if clase.estado_inscipcion == 'Rechazado' and clase.abierta:
                cantidad_de_clases_rechazado += 1
        return cantidad_de_clases_rechazado


class EstadoSolicitudUnirse(models.TextChoices):
    ACEPTADO = 'Aceptado', _('Aceptado')
    RECHAZADO = 'Rechazado', _('Rechazado')
    EN_ESPERA = 'En espera', _('En espera')


class Inscripcion(models.Model):
    """
    Representa la inscripción de un alumno a una clase
    """
    aceptado = models.CharField(max_length=9, choices=EstadoSolicitudUnirse.choices,
                                default=EstadoSolicitudUnirse.EN_ESPERA)
    alumno = models.ForeignKey(Alumno, on_delete=models.RESTRICT)
    clase = models.ForeignKey(Clase, on_delete=models.RESTRICT)
