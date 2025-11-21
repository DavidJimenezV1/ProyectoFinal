from django import forms
from .models import Auditoria


class AuditoriaFilterForm(forms.Form):
    """Formulario para filtrar auditorías"""
    
    ACCION_CHOICES = [
        ('', 'Todas las acciones'),
        ('CREATE', 'Creaciones'),
        ('UPDATE', 'Actualizaciones'),
        ('DELETE', 'Eliminaciones'),
    ]
    
    accion = forms.ChoiceField(
        choices=ACCION_CHOICES,
        required=False,
        label='Tipo de acción',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    fecha_desde = forms.DateField(
        required=False,
        label='Fecha desde',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        label='Fecha hasta',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    usuario = forms.CharField(
        required=False,
        label='Usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por usuario...'
        })
    )
    
    buscar = forms.CharField(
        required=False,
        label='Buscar',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar en auditorías...'
        })
    )
