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

    def cantidad_de_entregas(self):
        """ Cuenta la cantidad de entregas realizadas"""
        return self.entrega_set.count()


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
    revision = models.OneToOneField(Revision, on_delete=models.RESTRICT, null=True)
    alumno = models.ForeignKey(Alumno, on_delete=models.RESTRICT)
    actvidad = models.ForeignKey(Actividad, on_delete=models.RESTRICT)


class Archivo(models.Model):
    """
    Es un archivo el cual puede subir un alumno a su actividad
    """
    entrega = models.ForeignKey(Entrega, on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='entregas')

    def extension(self):
        extension = self.archivo.name.split('.')[-1]
        tipo_archivo = 'otro'
        if extension == 'pdf':
            tipo_archivo = 'pdf'
        if extension == 'doc':
            tipo_archivo = 'word'
        if extension == 'jpg' or extension == 'png' or extension == 'gif':
            tipo_archivo = 'imagen'
        if extension == 'avi' or extension == 'mp4' or extension == 'mkv' or extension == 'fvl' or extension == 'wmv':
            tipo_archivo = 'video'
        return tipo_archivo

    def nombre(self):
        nombre = self.archivo.name
        if len(nombre) > 18:
            nombre = "..." + nombre[-18:]
        return nombre.split('/')[-1]
