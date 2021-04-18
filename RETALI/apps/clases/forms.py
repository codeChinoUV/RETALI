from django import forms

from apps.clases.models import Clase


class ClaseForm(forms.ModelForm):
    foto = forms.ImageField(required=True, label='Foto',
                            widget=forms.ClearableFileInput(attrs={'class': "custom-file-input"}))

    class Meta:
        model = Clase
        fields = ['nombre', 'escuela']

        labels = {
            'nombre': 'Nombre de la clase',
            'escuela': 'Escuela',
        }

        widgets = {
            'nombre': forms.TextInput(attrs={'class': "form-control", 'placeholder': "Ingrese el nombre de su clase"}),
            'escuela': forms.TextInput(attrs={'class': "form-control",
                                              'placeholder': "Ingrese el nombre de la escuela a la que pertecene"}),
        }
