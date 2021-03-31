import io
import os
import sys
from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import models
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

logger = get_task_logger(__name__)


def obtener_path_de_subida(instance, filename):
    """define el path en donde se guardara la imagen en base al nombre de la clase que tenga relacionada"""
    objeto = instance._meta.fields_map
    model = objeto[list(objeto.keys())[0]].related_model._meta
    name = model.verbose_name_plural.replace(' ', '_')
    return f'{name}/images/{filename}'


class EstadoConvercionImagenes(models.TextChoices):
    """ Representa los diferentes estados que puede tener la conversión de las imagenes a las diferentes calidades"""
    SIN_CONVERTIR = 'SIN_CONVERTIR'
    EN_PROCESO = 'EN_PROCESO'
    EN_ERROR = 'EN_ERROR'
    CONVERTIDA = 'CONVERTIDA'


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
    estado_convercion = models.CharField(max_length=13, choices=EstadoConvercionImagenes.choices,
                                         default=EstadoConvercionImagenes.SIN_CONVERTIR)

    def guardar_imagen_original(self, imagen):
        self.imagen_original = imagen
        self.save()
        ImagenConCalidades.crear_calidades.delay(self.pk)

    def __validar_calidades_de_imagen_disponibles(self):
        """
        Valida si las calidades de las imagenes se encuentran disponibles, de no ser así empieza a realizar la
        conversión
        """
        if self.estado_convercion != EstadoConvercionImagenes.CONVERTIDA and self.estado_convercion \
                != EstadoConvercionImagenes.EN_PROCESO:
            ImagenConCalidades.crear_calidades.delay(self.pk)

    def obtener_imagen_calidad_alta(self):
        """Recupera la imagen con calidad alta"""
        self.__validar_calidades_de_imagen_disponibles()
        if self.imagen_calidad_alta:
            return self.imagen_calidad_alta

    def obtener_imagen_calidad_media(self):
        """Recupera la imagen con calidad media"""
        self.__validar_calidades_de_imagen_disponibles()
        if self.imagen_calidad_media:
            return self.imagen_calidad_media

    def obtener_imagen_calidad_baja(self):
        """Recupera la imagen con calidad baja"""
        self.__validar_calidades_de_imagen_disponibles()
        if self.imagen_calidad_baja:
            return self.imagen_calidad_alta

    @staticmethod
    @shared_task(auto_retry=[Exception], max_retries=4)
    def crear_calidades(id_imagen_con_calidades: int):
        """Crea imagenes de diferentes resoluciones de una Imagen"""
        imagen_con_calidades = ImagenConCalidades.objects.filter(pk=id_imagen_con_calidades).first()
        try:
            imagen_con_calidades.estado_convercion = EstadoConvercionImagenes.EN_PROCESO
            imagen_con_calidades.save()
            imagen = imagen_con_calidades.imagen_original
            path, file = os.path.split(imagen.path)
            file_name, ext = os.path.splitext(file)
            ext = ext.replace('.', '')
            logger.info(f'Se ha empezado a convertir la imagen con id {id_imagen_con_calidades}')
            stream = imagen.open()
            imagen_bytes = Image.open(stream)
            imagen_calidad_alta = ImagenConCalidades._crear_imagen(imagen_bytes, file_name, ext,
                                                                   imagen_con_calidades.__class__.
                                                                   RESOLUCION_CALIDAD_ALTA[0],
                                                                   imagen_con_calidades.__class__.
                                                                   RESOLUCION_CALIDAD_ALTA[1],
                                                                   imagen_con_calidades.__class__.CALIDAD_IMAGENES)
            imagen_con_calidades.imagen_calidad_alta = imagen_calidad_alta
            imagen_calidad_media = ImagenConCalidades._crear_imagen(imagen_bytes, file_name, ext,
                                                                    imagen_con_calidades.__class__.
                                                                    RESOLUCION_CALIDAD_MEDIA[0],
                                                                    imagen_con_calidades.__class__.
                                                                    RESOLUCION_CALIDAD_MEDIA[1],
                                                                    imagen_con_calidades.__class__.CALIDAD_IMAGENES)
            imagen_con_calidades.imagen_calidad_media = imagen_calidad_media
            imagen_calidad_baja = ImagenConCalidades._crear_imagen(imagen_bytes, file_name, ext,
                                                                   imagen_con_calidades.__class__.
                                                                   RESOLUCION_CALIDAD_BAJA[0],
                                                                   imagen_con_calidades.__class__.
                                                                   RESOLUCION_CALIDAD_BAJA[1],
                                                                   imagen_con_calidades.__class__.CALIDAD_IMAGENES)
            imagen_con_calidades.imagen_calidad_baja = imagen_calidad_baja
            imagen_con_calidades.estado_convercion = EstadoConvercionImagenes.CONVERTIDA
            imagen_con_calidades.save()
            logger.info(f'Se ha terminado de convertir las calidades de la imagen con id {id_imagen_con_calidades}')
        except Exception as e:
            imagen_con_calidades.estado_convercion = EstadoConvercionImagenes.EN_ERROR
            imagen_con_calidades.save()
            logger.error(f'Ocrrio un error al convertir la imagen con id {id_imagen_con_calidades}: {e}')

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
