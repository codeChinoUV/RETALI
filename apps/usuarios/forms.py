from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario, Persona
from ..clases.models import Maestro, Alumno


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = Usuario
        fields = ('email',)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = Usuario
        fields = ('email',)


class UsuarioForm(forms.ModelForm):
    repeticion_contrasenia = forms.CharField(label='Confirmación de contraseña',
                                             widget=forms.PasswordInput(
                                                 attrs={'class': 'form-control', 'placeholder': 'Repite tu contraseña'})
                                             )

    class Meta:
        model = Usuario
        fields = ['email', 'es_maestro', 'password']

        labels = {
            'email': _('Correo electronico'),
            'es_maestro': _('Soy maestro'),
            'password': _('Contraseña'),
        }

        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Introduce tu contraseña'}),
        }

    def clean_repeticion_contrasenia(self):
        contrasenia = self.cleaned_data['password']
        repeticion = self.cleaned_data['repeticion_contrasenia']
        if repeticion != contrasenia:
            raise ValidationError('Las contraseñas no coinciden')
        return repeticion

    def save(self, commit=True):
        usuario = super(UsuarioForm, self).save(commit=False)
        usuario.set_password(self.cleaned_data['password'])
        if commit:
            usuario.save()
        return usuario


class PersonaForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = [
            'nombre',
            'apellidos',
            'numero_telefonico',
            'foto_de_perfil'
        ]

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Introduce tu nombre'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Introduce tus apellidos'}),
            'numero_telefonico': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Introduce tu numero telefonico'}),
        }

    def save(self, commit=True):
        datos = self.cleaned_data
        if self.instance.usuario.es_maestro:
            usuario_registrado = Maestro(nombre=datos['nombre'], apellidos=datos['apellidos'],
                                         numero_telefonico=datos['numero_telefonico'], usuario=self.instance.usuario)
            usuario_registrado.save()
        else:
            usuario_registrado = Alumno(nombre=datos['nombre'], apellidos=datos['apellidos'],
                                        numero_telefonico=datos['numero_telefonico'], usuario=self.instance.usuario)
            usuario_registrado.save()
        return usuario_registrado
