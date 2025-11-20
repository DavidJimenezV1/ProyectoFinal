from django import forms
from django.forms import inlineformset_factory
from .models import Pedido, DetallePedido

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['cliente', 'fecha_entrega', 'estado', 'observaciones']
        widgets = {
            'fecha_entrega': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class DetallePedidoForm(forms.ModelForm):
    class Meta:
        model = DetallePedido
        fields = ['producto', 'cantidad', 'precio_unitario']
        widgets = {
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control'}),
            'producto': forms.Select(attrs={'class': 'form-control'}),
        }

PedidoLineaFormSet = inlineformset_factory(
    Pedido, DetallePedido, form=DetallePedidoForm,
    extra=1, can_delete=True
)
