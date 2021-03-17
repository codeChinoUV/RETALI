from django import forms
from django.core.exceptions import ValidationError

from apps.actividades.models import Actividad


class DateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'


class ActividadForm(forms.ModelForm):
    """
    Formulario que servira para registrar una actividad, ademas de servir para validar los campos
    """

    class Meta:
        model = Actividad
        fields = ['nombre', 'descripcion', 'fecha_de_inicio', 'fecha_de_cierre']
        labels = {
            'nombre': 'Nombre de la actividad:',
            'descripcion': 'Descripcion de la actividad:',
            'fecha_de_inicio': 'Fecha de apertura:',
            'fecha_de_cierre': 'Fecha de cierre:'
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': "form-control"}),
            'descripcion': forms.Textarea(attrs={'class': "form-control"}),
            'fecha_de_inicio': DateTimeInput(attrs={'class': "form-control"}),
            'fecha_de_cierre': DateTimeInput(attrs={'class': "form-control"})
        }

    def clean_fecha_de_cierre(self):
        fecha_inicio = self.cleaned_data['fecha_de_inicio']
        fecha_cierre = self.cleaned_data['fecha_de_cierre']
        if fecha_cierre < fecha_inicio:
            raise ValidationError('La fecha de apertura de la actividad no puede ser despues a la de cierre')
        return fecha_cierre


class ActividadDisableForm(forms.ModelForm):
    """
    Formulario que servira para mostrar una actividad
    """

    class Meta:
        model = Actividad
        fields = ['nombre', 'descripcion', 'fecha_de_inicio', 'fecha_de_cierre']
        labels = {
            'nombre': 'Nombre de la actividad:',
            'descripcion': 'Descripcion de la actividad:',
            'fecha_de_inicio': 'Fecha de apertura:',
            'fecha_de_cierre': 'Fecha de cierre:'
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': "form-control", 'disabled': ''}),
            'descripcion': forms.Textarea(attrs={'class': "form-control", 'disabled': ''}),
            'fecha_de_inicio': DateTimeInput(attrs={'class': "form-control", 'disabled': ''}),
            'fecha_de_cierre': DateTimeInput(attrs={'class': "form-control", 'disabled': ''})
        }