from django import forms


class DateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'


class ActividadForm(forms.Form):
    """
    Formulario que servira para registrar una actividad, ademas de servir para validar los campos
    """
    nombre = forms.CharField(max_length=120, required=True, label='Nombre de la actividad:',
                             widget=forms.TextInput(attrs={'class': "form-control"}))
    descripcion = forms.CharField(required=True, label='Descripcion de la actividad:',
                                  widget=forms.Textarea(attrs={'class': "form-control"}))
    fecha_inicio = forms.DateTimeField(required=True, label='Fecha de inicio:', input_formats=['%d/%m/%Y %H:%M'],
                                       widget=DateTimeInput(attrs={'class': "form-control"}))
    fecha_cierre = forms.DateTimeField(required=True, label='Fecha de cierre:', input_formats=['%d/%m/%Y %H:%M'],
                                       widget=DateTimeInput(attrs={'class': "form-control"}))
