"""
Autor: José Miguel Quiroz Benitez
Fecha de creación: 22-03-2021
Ultima actualización: 22-03-2021
"""
import os
from zipfile import ZipFile

from celery import shared_task
from django.conf import settings
from PIL import Image

@shared_task()
def make_thumbnails(imagen: Image, thumbnails: []):
    path, file = os.path.split(imagen.path)
    file_name, ext = os.path.splitext(file)
    stream = imageField.open()
    imagen_bytes = Image.open(stream)
    imagenes_generadas = []
    for w, h in thumbnails:
        img_copy = imagen_bytes.copy()
        img_copy.thumbnail((w,h))
        img_copy_path = f'{file_name}_{w}_{h}.{ext}'
        imagenes_generadas.append({'nombre': img_copy_path, 'archivo': img_copy})
    imagen.close()
    return imagenes_generadas



#@shared_task()
#def make_thumbnails(file_path, thumbnails=[] ):
#    os.chdir(os.path.join(settings.MEDIA_ROOT, 'clases'))
#    path, file = os.path.split(file_path)
#    file_name, ext = os.path.splitext(file)
#
#    zip_file = f"{file_name}.zip"
#    results = {'archive_path': f"{settings.MEDIA_URL}clases/{zip_file}"}
#    try:
#        img = Image.open(file_path)
#        zipper = ZipFile(zip_file, 'w')
#        zipper.write(file)
#        os.remove(file_path)
#        for w, h in thumbnails:
#            img_copy = img.copy()
#            img_copy.thumbnail((w,h))
#            thumbnail_file = f'{file_name}_{w}_{h}.{ext}'
#            img_copy.save(thumbnail_file)
#            zipper.write(thumbnail_file)
#            os.remove(thumbnail_file)
#        img.close()
#        zipper.close()
#    except IOError as e:
#        print(e)
#    return results
