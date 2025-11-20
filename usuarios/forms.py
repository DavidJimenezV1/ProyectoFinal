from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario

class RegistroClienteForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo Electrónico")
    first_name = forms.CharField(required=True, label="Nombre")
    last_name = forms.CharField(required=True, label="Apellido")
    telefono = forms.CharField(required=True, label="Teléfono")
    direccion = forms.CharField(required=True, widget=forms.Textarea, label="Dirección")
    empresa = forms.CharField(required=False, label="Empresa (Opcional)")
    
    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'telefono', 'direccion', 'empresa', 'password1', 'password2'
        ]

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Usuario o Email")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)