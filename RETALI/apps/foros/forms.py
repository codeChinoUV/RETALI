from django import forms
from django.core.exceptions import ValidationError

from apps.foros.models import Foro


class DateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'


class ForoForm(forms.ModelForm):
    """
    Formulario que servira para registrar un foro, ademas de servir para validar los campos
    """

    class Meta:
        model = Foro
        fields = ['nombre', 'descripcion', 'fecha_de_inicio', 'fecha_de_cierre']
        labels = {
            'nombre': 'Nombre del foro:',
            'descripcion': 'Descripcion del foro:',
            'fecha_de_inicio': 'Fecha de inicio:',
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
