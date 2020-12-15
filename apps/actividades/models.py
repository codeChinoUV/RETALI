from django.db import models
from django.utils import timezone

from apps.clases.models import Clase


class Actividad(models.Model):
    """
    Representa una actividad que crea el maestro
    """
    descripcion = models.TextField(null=False)
    fecha_de_inicio = models.DateTimeField(null=False)
    fecha_de_cierre = models.DateTimeField(null=False)
    nombre = models.CharField(max_length=120, null=False)
    clase = models.ForeignKey(Clase, on_delete=models.RESTRICT)
    abierta = models.BooleanField(default=True)


class Revision(models.Model):
    """
    Representa la revisión realizada por el maestro de la entrega de una Actividad de un Alumno
    """
    calificacion = models.FloatField(null=False)
    retroalimentacion = models.TextField()


class Entrega(models.Model):
    """
    Representa la entrega de la actividad de un Alumno
    """
    comentarios = models.TextField(null=True)
    fecha_de_entrega = models.DateTimeField(default=timezone.now)
    revision = models.OneToOneField(Revision, on_delete=models.RESTRICT)
    entrega = models.FileField(upload_to='entregas')

