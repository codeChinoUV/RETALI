from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.usuarios.models import Persona


class Maestro(Persona):
    """
    Representa al usuario Maestro
    """
    informacion = models.TextField()


class Clase(models.Model):
    """
    Contiene la información de la clase, asi como el codigo para unirse a la clase
    """
    codigo = models.CharField(max_length=10, db_index=True)
    escuela = models.CharField(max_length=100, null=False)
    nombre = models.CharField(max_length=120, null=False)
    abierta = models.BooleanField(default=True)
    foto = models.ImageField(upload_to='clases')
    maestro = models.ForeignKey(Maestro, on_delete=models.RESTRICT)


class Alumno(Persona):
    """
    Representa un alumno en el sistema
    """
    inscripciones = models.ManyToManyField(Clase, through='Inscripcion')


class Inscripcion(models.Model):
    """
    Representa la inscripción de un alumno a una clase
    """
    class EstadoSolicitudUnirse(models.TextChoices):
        ACEPTADO = 'Aceptado', _('Aceptado')
        RECHAZADO = 'Rechazado', _('Rechazado')
        EN_ESPERA =  'En espera', _('En espera')
    aceptado = models.CharField(max_length=9, choices=EstadoSolicitudUnirse.choices,
                                default=EstadoSolicitudUnirse.EN_ESPERA)
    alumno = models.ForeignKey(Alumno, on_delete=models.RESTRICT)
    clase = models.ForeignKey(Clase, on_delete=models.RESTRICT)
