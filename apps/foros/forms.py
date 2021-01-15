from django import forms


class DateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'


class ForoForm(forms.Form):
    """
    Formulario que servira para registrar un foro, ademas de servir para validar los campos
    """
    nombre = forms.CharField(max_length=80, required=True, label='Nombre del foro:',
                             widget=forms.TextInput(attrs={'class': "form-control"}))
    descripcion = forms.CharField(required=True, label='Descripcion del foro:',
                                  widget=forms.Textarea(attrs={'class': "form-control"}))
    fecha_inicio = forms.DateTimeField(required=True, label='Fecha de inicio:',
                                       widget=DateTimeInput(attrs={'class': "form-control"}))
    fecha_cierre = forms.DateTimeField(required=True, label='Fecha de cierre:',
                                       widget=DateTimeInput(attrs={'class': "form-control"}))
