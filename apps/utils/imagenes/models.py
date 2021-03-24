from enum import Enum

from django.core.files import File
from django.db import models


# Falta guardar las imagenes en una carpeta diferente por id
def obtener_path_de_subida(instance, filename):
    clases = instance.album.__class__._meta.fields_map
    model = clases[list(clases.keys())[0]].related_model._meta
    name = model.verbose_name_plural.replace(' ', '_')
    return f'{name}/images/{filename}'


class ImagenAlbum(models.Model):
    def original(self):
        return self.imagen_set.filter(original=True).first()

    def calidades(self):
        return self.imagen_set.filter(original=False).all()


class Imagen(models.Model):
    name = models.CharField(max_length=255)
    imagen = models.ImageField(upload_to=obtener_path_de_subida)
    original = models.BooleanField(default=False)
    width = models.FloatField(default=100)
    height = models.FloatField(default=100)
    album = models.ForeignKey(ImagenAlbum, related_name='images',
                              on_delete=models.CASCADE)
