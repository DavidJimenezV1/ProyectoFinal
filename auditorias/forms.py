from django import forms
from auditorias.models import AuditLog

class AuditLogSearchForm(forms.Form):
    """Formulario de búsqueda avanzada para auditoría"""
    
    RANGE_CHOICES = [
        ('', '--- Seleccionar ---'),
        ('today', 'Hoy'),
        ('7days', 'Últimos 7 días'),
        ('30days', 'Últimos 30 días'),
        ('year', 'Últimos 365 días'),
    ]
    
    ACTION_CHOICES = [
        ('', '--- Seleccionar ---'),
        ('CREATE', 'Crear'),
        ('UPDATE', 'Actualizar'),
        ('DELETE', 'Eliminar'),
        ('VIEW', 'Ver'),
    ]
    
    fecha_rango = forms.ChoiceField(
        choices=RANGE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    accion = forms.ChoiceField(
        choices=ACTION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    modelo = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Producto, Pedido...'
        })
    )
    
    usuario = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario'
        })
    )
    
    busqueda = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar en descripción...'
        })
    )