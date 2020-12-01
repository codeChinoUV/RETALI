from django.db import models
from django.utils import timezone

from apps.clases.models import Clase, Alumno


class Aviso(models.Model):
    """
    Representa un aviso que realiza un maestro a sus alumnos
    """
    nombre = models.CharField(max_length=120, null=False)
    descripcion = models.TextField(null=False)
    fecha_publicado = models.DateTimeField(default=timezone.now)
    clase = models.ForeignKey(Clase, on_delete=models.RESTRICT)
    leido_por = models.ManyToManyField(Alumno)
