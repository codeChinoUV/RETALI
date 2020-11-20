from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from apps.usuarios.models import Persona


class Maestro(Persona):
    informacion = models.TextField()


class Clase(models.Model):
    codigo = models.CharField(max_length=10, db_index=True)
    escuela = models.CharField(max_length=100, null=False)
    nombre = models.CharField(max_length=120, null=False)
    abierta = models.BooleanField(default=True)
    foto = models.ImageField(upload_to='clases')
    maestro = models.ForeignKey(Maestro, on_delete=models.RESTRICT)


class Alumno(Persona):
    inscripciones = models.ManyToManyField(Clase, through='Inscripcion')


class Actividad(models.Model):
    descripcion = models.TextField(null=False)
    fecha_de_inicio = models.DateTimeField(null=False)
    fecha_de_cierre = models.DateTimeField(null=False)
    nombre = models.CharField(max_length=120, null=False)
    clase = models.ForeignKey(Clase, on_delete=models.RESTRICT)


class Foro(models.Model):
    class EstadoForo(models.TextChoices):
        ABIERTO = 'Abierto', _('Abierto')
        CERRADO = 'Cerrado', _('Cerrado')

    nombre = models.CharField(max_length=120, null=False)
    descripcion = models.TextField(null=False)
    estado = models.CharField(max_length=7, choices=EstadoForo.choices, default=EstadoForo.ABIERTO)
    fecha_de_inicio = models.DateTimeField(null=False)
    fecha_de_cierre = models.DateTimeField(null=False)
    clase = models.ForeignKey(Clase, on_delete=models.RESTRICT)
    participaciones = models.ManyToManyField(Persona, through='Participacion')


class Aviso(models.Model):
    nombre = models.CharField(max_length=120, null=False)
    descripcion = models.TextField(null=False)
    fecha_publicado = models.DateTimeField(default=timezone.now)
    clase = models.ForeignKey(Clase, on_delete=models.RESTRICT)
    leido_por = models.ManyToManyField(Alumno)


class Inscripcion(models.Model):
    aceptado = models.BooleanField(default=False)
    alumno = models.ForeignKey(Alumno, on_delete=models.RESTRICT)
    clase = models.ForeignKey(Clase, on_delete=models.RESTRICT)


class Participacion(models.Model):
    participante = models.ForeignKey(Persona, on_delete=models.RESTRICT)
    foro = models.ForeignKey(Foro, on_delete=models.RESTRICT)
    fecha = models.DateTimeField(default=timezone.now)
    participacion = models.TextField(null=False)


class Revision(models.Model):
    calificacion = models.FloatField(null=False)
    retroalimentacion = models.TextField()


class Entrega(models.Model):
    fecha_de_entrega = models.DateTimeField(default=timezone.now)
    revision = models.OneToOneField(Revision, on_delete=models.RESTRICT)


class Archivo(models.Model):
    ruta = models.CharField(max_length=100, null=False)
    extension = models.CharField(max_length=10)
    entrega = models.ForeignKey(Entrega, on_delete=models.RESTRICT)
