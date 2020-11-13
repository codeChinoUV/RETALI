from django.db import models

from apps.usuarios.models import Persona


class Maestro(Persona):
    informacion = models.TextField()


class Clase(models.Model):
    codigo = models.CharField(max_length=10, db_index=True)
    escuela = models.CharField(max_length=100, null=False)
    nombre = models.CharField(max_length=120, null=False)
    numero_de_telefono = models.CharField(max_length=10)
    maestro = models.ForeignKey(Maestro, on_delete=models.RESTRICT)


class Alumno(Persona):
    inscripciones = models.ManyToManyField(Clase, through='Inscripcion')


class Inscripcion(models.Model):
    aceptado = models.BooleanField(default=False)
    alumno = models.ForeignKey(Alumno, on_delete=models.RESTRICT)
    clase = models.ForeignKey(Clase, on_delete=models.RESTRICT)
