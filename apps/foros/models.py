from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.clases.models import Clase
from apps.usuarios.models import Persona
from django.utils import timezone


class Foro(models.Model):
    """
    Representa un foro para que los alumnos puedan participar
    """

    class EstadoForo(models.TextChoices):
        ABIERTO = 'Abierto', _('Abierto')
        CERRADO = 'Cerrado', _('Cerrado')
        POR_ABRIR = 'Por abrir', _('Por abrir')

    nombre = models.CharField(max_length=120, null=False)
    descripcion = models.TextField(null=False)
    estado = models.CharField(max_length=9, choices=EstadoForo.choices, default=EstadoForo.ABIERTO)
    fecha_de_inicio = models.DateTimeField(null=False)
    fecha_de_cierre = models.DateTimeField(null=False)
    fecha_de_creacion = models.DateTimeField(default=timezone.now)
    clase = models.ForeignKey(Clase, on_delete=models.RESTRICT)
    participaciones = models.ManyToManyField(Persona, through='Participacion')
    eliminado = models.BooleanField(default=False)


class Participacion(models.Model):
    """
    Representa la participación de un Alumno en un Foro
    """
    participante = models.ForeignKey(Persona, on_delete=models.RESTRICT)
    foro = models.ForeignKey(Foro, on_delete=models.RESTRICT)
    fecha = models.DateTimeField(default=timezone.now)
    participacion = models.TextField(null=False)
    eliminada = models.BooleanField(default=True)


class Respuesta(models.Model):
    """
    Representa una respuesta a una participación
    """
    foro = models.ForeignKey(Foro, on_delete=models.CASCADE)
    numero_respuesta = models.IntegerField(null=False)
    fecha = models.DateTimeField(default=timezone.now)
    respuesta = models.TextField(null=False)
    eliminada = True
