from django import forms

from apps.clases.models import Clase


class ClaseForm(forms.ModelForm):
    class Meta:
        model = Clase
        fields = ['nombre', 'escuela', 'foto']

        labels = {
            'nombre': 'Nombre de la clase',
            'escuela': 'Escuela',
            'foto': 'Foto'
        }

        widgets = {
            'nombre': forms.TextInput(attrs={'class': "form-control", 'placeholder': "Ingrese el nombre de su clase"}),
            'escuela': forms.TextInput(attrs={'class': "form-control",
                                             'placeholder': "Ingrese el nombre de la escuela a la que pertecene"}),
            'foto': forms.ClearableFileInput(attrs={'class': "custom-file-input"})
        }
