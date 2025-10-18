from django import forms
from django.forms import inlineformset_factory
from .models import Cotizacion, DetalleCotizacion

class CotizacionForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        fields = ['notas_cliente']
        widgets = {
            'notas_cliente': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Añade cualquier detalle o requisito especial para tu cotización...'}),
        }

class DetalleCotizacionForm(forms.ModelForm):
    class Meta:
        model = DetalleCotizacion
        fields = ['producto', 'cantidad', 'notas']
        widgets = {
            'notas': forms.TextInput(attrs={'placeholder': 'Ej: Color específico, tamaño personalizado...'}),
        }

# Formset para manejar múltiples items de cotización
DetalleCotizacionFormSet = inlineformset_factory(
    Cotizacion, 
    DetalleCotizacion,
    form=DetalleCotizacionForm,
    extra=1,
    can_delete=True
)