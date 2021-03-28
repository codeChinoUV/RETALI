import io
import os
import sys
from celery import shared_task
from django.db import models
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile


def obtener_path_de_subida(instance, filename):
    """define el path en donde se guardara la imagen en base al nombre de la clase que tenga relacionada"""
    objeto = instance._meta.fields_map
    model = objeto[list(objeto.keys())[0]].related_model._meta
    name = model.verbose_name_plural.replace(' ', '_')
    return f'{name}/images/{filename}'


class ImagenConCalidades(models.Model):
    """ Clase para almacenar una imagen con sus diferentes resoluciones"""
    RESOLUCION_CALIDAD_BAJA = (128, 128)
    RESOLUCION_CALIDAD_MEDIA = (384, 384)
    RESOLUCION_CALIDAD_ALTA = (768, 768)
    CALIDAD_IMAGENES = 95

    imagen_original = models.ImageField(upload_to=obtener_path_de_subida)
    imagen_calidad_alta = models.ImageField(upload_to=obtener_path_de_subida, null=True)
    imagen_calidad_media = models.ImageField(upload_to=obtener_path_de_subida, null=True)
    imagen_calidad_baja = models.ImageField(upload_to=obtener_path_de_subida, null=True)

    def guardar_imagen_original(self, imagen):
        self.imagen_original = imagen
        self.save()
        ImagenConCalidades.crear_calidades.delay(self.pk)

    def obtener_imagen_calidad_alta(self):
        """Recupera la imagen con calidad alta"""
        if self.imagen_calidad_alta:
            return self.imagen_calidad_alta

    def obtener_imagen_calidad_media(self):
        """Recupera la imagen con calidad media"""
        if self.imagen_calidad_media:
            return self.imagen_calidad_media

    def obtener_imagen_calidad_baja(self):
        """Recupera la imagen con calidad baja"""
        if self.imagen_calidad_baja:
            return self.imagen_calidad_alta

    @shared_task()
    def crear_calidades(id_imagen_con_calidades: int):
        """Crea imagenes de diferentes resoluciones de una Imagen"""
        imagen_con_calidades = ImagenConCalidades.objects.filter(pk=id_imagen_con_calidades).first()
        imagen = imagen_con_calidades.imagen_original
        path, file = os.path.split(imagen.path)
        file_name, ext = os.path.splitext(file)
        ext = ext.replace('.', '')
        stream = imagen.open()
        imagen_bytes = Image.open(stream)
        imagen_calidad_alta = ImagenConCalidades._crear_imagen(imagen_bytes, file_name, ext,
                                                               imagen_con_calidades.__class__.RESOLUCION_CALIDAD_ALTA[
                                                                   0],
                                                               imagen_con_calidades.__class__.RESOLUCION_CALIDAD_ALTA[
                                                                   1],
                                                               imagen_con_calidades.__class__.CALIDAD_IMAGENES)
        imagen_con_calidades.imagen_calidad_alta = imagen_calidad_alta
        imagen_calidad_media = ImagenConCalidades._crear_imagen(imagen_bytes, file_name, ext,
                                                                imagen_con_calidades.__class__.RESOLUCION_CALIDAD_MEDIA[
                                                                    0],
                                                                imagen_con_calidades.__class__.RESOLUCION_CALIDAD_MEDIA[
                                                                    1],
                                                                imagen_con_calidades.__class__.CALIDAD_IMAGENES)
        imagen_con_calidades.imagen_calidad_media = imagen_calidad_media
        imagen_calidad_baja = ImagenConCalidades._crear_imagen(imagen_bytes, file_name, ext,
                                                               imagen_con_calidades.__class__.RESOLUCION_CALIDAD_BAJA[
                                                                   0],
                                                               imagen_con_calidades.__class__.RESOLUCION_CALIDAD_BAJA[
                                                                   1],
                                                               imagen_con_calidades.__class__.CALIDAD_IMAGENES)
        imagen_con_calidades.imagen_calidad_baja = imagen_calidad_baja
        imagen_con_calidades.save()

    @staticmethod
    def _crear_imagen(imagen_original, nombre_archivo, extension, alto, ancho, calidad):
        """ Crea una copia de una imagen con un ancho y alto especifico"""
        img_copy = imagen_original.copy()
        img_copy.thumbnail((ancho, alto))
        img_copy_path = f'{nombre_archivo}_{ancho}_{alto}.{extension}'
        output = io.BytesIO()
        img_copy.save(output, format='JPEG', quality=calidad)
        output.seek(0)
        imagen_a_guardar = InMemoryUploadedFile(output, 'ImageField', img_copy_path, 'img/jpeg',
                                                sys.getsizeof(output), None)
        return imagen_a_guardar
