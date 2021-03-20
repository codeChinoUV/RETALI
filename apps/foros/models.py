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

    def actualizar_estado(self):
        """
        Actualiza el estado del foro
        :return: None
        """
        now = timezone.now()
        if self.fecha_de_inicio > now:
            self.estado = 'Por abrir'
        elif self.fecha_de_cierre < now:
            self.estado = 'Cerrada'
        else:
            self.estado = 'Abierta'
        self.save()

    def cantidad_de_participaciones(self):
        """
        Obtiene la cantidad de participaciones de un foro
        :return: La cantidad de participaciones
        """
        return self.participacion_set.filter(eliminada=False).count()

    def obtener_participaciones(self):
        """
        Obtiene las participaciones del foro que no esten eliminadas
        :return: Una lista de participaciones
        """
        return self.participacion_set.filter(eliminada=False).all()


class Participacion(models.Model):
    """
    Representa la participación de un Alumno en un Foro
    """
    participante = models.ForeignKey(Persona, on_delete=models.RESTRICT)
    foro = models.ForeignKey(Foro, on_delete=models.RESTRICT)
    fecha = models.DateTimeField(default=timezone.now)
    participacion = models.TextField(null=False)
    eliminada = models.BooleanField(default=False)

    def obtener_respuestas(self):
        """
        Obtiene la lista de respuesta de la participación que no esten eliminadas
        """
        return self.respuesta_set.filter(eliminada=False).all()


class Respuesta(models.Model):
    """
    Representa una respuesta a una participación
    """
    participacion = models.ForeignKey(Participacion, on_delete=models.CASCADE)
    numero_respuesta = models.IntegerField(null=False)
    fecha = models.DateTimeField(default=timezone.now)
    respuesta = models.TextField(null=False)
    autor = models.ForeignKey(Persona, on_delete=models.RESTRICT)
    eliminada = models.BooleanField(default=False)
