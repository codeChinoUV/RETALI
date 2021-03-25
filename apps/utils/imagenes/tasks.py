"""
Autor: José Miguel Quiroz Benitez
Fecha de creación: 22-03-2021
Ultima actualización: 22-03-2021
"""
import io
import os
import sys

from celery import shared_task
from django.conf import settings
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

from apps.utils.imagenes.models import Imagen


RESOLUCION_CALIDAD_BAJA = (128, 128)
RESOLUCION_CALIDAD_MEDIA = (384, 384)
RESOLUCION_CALIDAD_ALTA = (768, 768)

CALIDAD_IMAGENES = 75

LISTA_RESOLUCIONES = [RESOLUCION_CALIDAD_ALTA, RESOLUCION_CALIDAD_MEDIA, RESOLUCION_CALIDAD_BAJA]


@shared_task()
def make_thumbnails(imagen_id: int, thumbnails: [] = LISTA_RESOLUCIONES, quality: int = CALIDAD_IMAGENES):
    """Crea imagenes de diferentes resoluciones de una Imagen"""
    objeto_imagen = Imagen.objects.filter(pk=imagen_id).first()
    imagen = objeto_imagen.imagen
    path, file = os.path.split(imagen.path)
    file_name, ext = os.path.splitext(file)
    ext = ext.replace('.', '')
    stream = imagen.open()
    imagen_bytes = Image.open(stream)
    for w, h in thumbnails:
        img_copy = imagen_bytes.copy()
        img_copy.thumbnail((w, h))
        img_copy_path = f'{file_name}_{w}_{h}.{ext}'
        output = io.BytesIO()
        img_copy.save(output, format='JPEG', quality=quality)
        output.seek(0)
        imagen_a_guardar = InMemoryUploadedFile(output, 'ImageField', img_copy_path, 'img/jpeg',
                                                sys.getsizeof(output), None)
        imagen_calidad_nueva = Imagen(height=h, width=w, name=img_copy_path, imagen=imagen_a_guardar,
                                      album_id=objeto_imagen.album_id)
        imagen_calidad_nueva.save()
    stream.close()
