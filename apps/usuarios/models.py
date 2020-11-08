from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import ugettext_lazy as _

from .managers import CustomUserManager


class Usuario(AbstractBaseUser, PermissionsMixin):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    es_maestro = models.BooleanField(default=False)
    eliminado = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Persona(models.Model):
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=120)
    numero_telefonico = models.CharField(max_length=13)
    foto_de_perfil = models.ImageField(upload_to='personas')
    usuario = models.OneToOneField(Usuario, on_delete=models.RESTRICT, primary_key=True)
