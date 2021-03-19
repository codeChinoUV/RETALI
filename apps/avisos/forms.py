from django import forms

from apps.avisos.models import Aviso


class AvisoForm(forms.ModelForm):
    """
    Formulario que servira para registrar una actividad, ademas de servir para validar los campos
    """
    class Meta:
        model = Aviso
        fields = ['nombre', 'descripcion']
        labels = {
            'nombre': 'Titulo del aviso:',
            'descripcion': 'Aviso:'
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': "form-control"}),
            'descripcion': forms.Textarea(attrs={'class': "form-control"})
        }
