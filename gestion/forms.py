# gestion/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Proyecto, Tarea, Mensaje, Comentario

# gestion/forms.py
from django import forms
from .models import Proyecto, Tarea, Mensaje, Comentario
from django.contrib.auth.models import User

from django import forms
from .models import Proyecto, Tarea, Mensaje, Comentario
from django.contrib.auth.models import User

class ProyectoForm(forms.ModelForm):
    usuarios = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = Proyecto
        fields = ['titulo', 'descripcion', 'fecha_inicio', 'fecha_fin', 'usuarios']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ['titulo', 'descripcion', 'fecha_limite', 'estado', 'asignados']
        widgets = {
            'fecha_limite': forms.DateInput(attrs={'type': 'date'}),
        }

class MensajeForm(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields = ['destinatario', 'contenido']
        widgets = {
            'destinatario': forms.Select(attrs={'class': 'form-control'}),
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['contenido']

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']