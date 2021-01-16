from django import forms


class AvisoForm(forms.Form):
    """
    Formulario que servira para registrar una actividad, ademas de servir para validar los campos
    """
    nombre = forms.CharField(max_length=50, required=True, label='Titulo del aviso:',
                             widget=forms.TextInput(attrs={'class': "form-control"}))
    descripcion = forms.CharField(required=True, label='Aviso:',
                                  widget=forms.Textarea(attrs={'class': "form-control"}))
