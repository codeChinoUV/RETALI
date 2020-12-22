from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.clases.models import Clase, Alumno


class Actividad(models.Model):
    """
    Representa una actividad que crea el maestro
    """
    class EstadoActividad(models.TextChoices):
        ABIERTA = 'Abierta', _('Abierta')
        CERRADA = 'Cerrada', _('Cerrada')
        POR_ABRIR = 'Por abrir', _('Por abrir')
    descripcion = models.TextField(null=False)
    fecha_de_inicio = models.DateTimeField(null=False)
    fecha_de_cierre = models.DateTimeField(null=False)
    nombre = models.CharField(max_length=120, null=False)
    clase = models.ForeignKey(Clase, on_delete=models.RESTRICT)
    estado = models.CharField(max_length=9, choices=EstadoActividad.choices, default=EstadoActividad.POR_ABRIR)
    fecha_de_creacion = models.DateTimeField(default=timezone.now)
    entregas = models.ManyToManyField(Alumno, through='Entrega')


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
    alumno = models.ForeignKey(Alumno, on_delete=models.RESTRICT)
    actvidad = models.ForeignKey(Actividad, on_delete=models.RESTRICT)


class Archivo(models.Model):
    """
    Es un archivo el cual puede subir un alumno a su actividad
    """
    entrega = models.ForeignKey(Entrega, on_delete=models.RESTRICT)
    archivo = models.FileField(upload_to='entregas')
