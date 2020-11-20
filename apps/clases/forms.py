from django import forms


class ClaseForm(forms.Form):
    nombre = forms.CharField(max_length=120, required=True, label='Nombre de la clase',
                             widget=forms.TextInput(attrs={'class': "form-control",
                                                           'placeholder': "Ingrese el nombre de su clase"}))
    escuela = forms.CharField(max_length=100, required=True, label='Escuela',
                              widget=forms.TextInput(attrs={'class': "form-control",
                                                            'placeholder': "Ingrese el nombre de la escuela a la que "
                                                                           "pertecene"}))
    foto = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class': "custom-file-input"}), label="Foto")

