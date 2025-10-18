from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone

from .models import Cotizacion, DetalleCotizacion
from inventario.models import Producto
from .forms import CotizacionForm, DetalleCotizacionFormSet

class CotizacionListView(LoginRequiredMixin, ListView):
    model = Cotizacion
    template_name = 'cotizaciones/lista_cotizaciones.html'
    context_object_name = 'cotizaciones'
    paginate_by = 10
    
    def get_queryset(self):
        # Si es admin, ver todas; si es cliente, solo las propias
        if self.request.user.es_admin:
            return Cotizacion.objects.all()
        return Cotizacion.objects.filter(cliente=self.request.user)

class CotizacionDetailView(LoginRequiredMixin, DetailView):
    model = Cotizacion
    template_name = 'cotizaciones/detalle_cotizacion.html'
    context_object_name = 'cotizacion'
    
    def get_object(self):
        obj = super().get_object()
        # Verificar que el usuario puede ver esta cotización
        if not self.request.user.es_admin and obj.cliente != self.request.user:
            raise HttpResponseForbidden("No tienes permiso para ver esta cotización.")
        return obj

@login_required
def nueva_cotizacion(request):
    """Vista para crear una nueva cotización"""
    if request.method == 'POST':
        form = CotizacionForm(request.POST)
        formset = DetalleCotizacionFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            # Guardar la cotización
            cotizacion = form.save(commit=False)
            cotizacion.cliente = request.user
            cotizacion.save()
            
            # Guardar los detalles
            for form_detalle in formset:
                if form_detalle.cleaned_data and not form_detalle.cleaned_data.get('DELETE', False):
                    detalle = form_detalle.save(commit=False)
                    detalle.cotizacion = cotizacion
                    detalle.save()
            
            messages.success(request, "Tu cotización ha sido enviada con éxito. Pronto nos pondremos en contacto contigo.")
            return redirect('cotizaciones:lista_cotizaciones')
    else:
        # Si se viene del catálogo con un producto específico
        producto_id = request.GET.get('producto_id')
        
        form = CotizacionForm()
        formset = DetalleCotizacionFormSet()
        
        if producto_id:
            # Pre-cargar el producto en el formulario
            try:
                producto = Producto.objects.get(id=producto_id)
                initial = [{'producto': producto, 'cantidad': 1}]
                formset = DetalleCotizacionFormSet(initial=initial)
            except Producto.DoesNotExist:
                pass
    
    return render(request, 'cotizaciones/crear_cotizacion.html', {
        'form': form,
        'formset': formset
    })

@login_required
def responder_cotizacion(request, pk):
    """Vista para que los administradores respondan a una cotización"""
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    
    if not request.user.es_admin:
        return HttpResponseForbidden("No tienes permiso para responder cotizaciones.")
        
    if request.method == 'POST':
        # Procesar la respuesta
        estado = request.POST.get('estado')
        notas_admin = request.POST.get('notas_admin')
        
        # Actualizar precios individuales
        for item in cotizacion.items.all():
            precio_str = request.POST.get(f'precio_{item.id}')
            if precio_str:
                try:
                    precio = float(precio_str)
                    item.precio_unitario = precio
                    item.save()
                except ValueError:
                    pass
        
        # Actualizar la cotización
        cotizacion.estado = estado
        cotizacion.notas_admin = notas_admin
        cotizacion.fecha_respuesta = timezone.now()
        cotizacion.save()
        
        messages.success(request, "La cotización ha sido actualizada correctamente.")
        return redirect('cotizaciones:detalle_cotizacion', pk=cotizacion.pk)
        
    return render(request, 'cotizaciones/responder_cotizacion.html', {
        'cotizacion': cotizacion
    })

@login_required
def nueva_cotizacion_desde_carrito(request):
    """Crear una cotización a partir del carrito actual"""
    carrito = request.session.get('carrito', {})
    
    if not carrito:
        messages.warning(request, 'Tu carrito de cotización está vacío')
        return redirect('catalogo:lista_productos')
    
    if request.method == 'POST':
        form = CotizacionForm(request.POST)
        
        if form.is_valid():
            # Guardar la cotización
            cotizacion = form.save(commit=False)
            cotizacion.cliente = request.user
            cotizacion.save()
            
            # Transferir productos del carrito a la cotización
            for producto_id, cantidad in carrito.items():
                try:
                    producto = Producto.objects.get(id=producto_id)
                    DetalleCotizacion.objects.create(
                        cotizacion=cotizacion,
                        producto=producto,
                        cantidad=cantidad,
                    )
                except Producto.DoesNotExist:
                    continue
            
            # Vaciar el carrito
            request.session['carrito'] = {}
            
            messages.success(request, "Tu cotización ha sido enviada con éxito. Pronto nos pondremos en contacto contigo.")
            return redirect('cotizaciones:lista_cotizaciones')
    else:
        form = CotizacionForm()
    
    # Obtener productos del carrito para mostrarlos
    items = []
    for producto_id, cantidad in carrito.items():
        try:
            producto = Producto.objects.get(id=producto_id)
            items.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': producto.precio * cantidad
            })
        except Producto.DoesNotExist:
            continue
    
    return render(request, 'cotizaciones/crear_desde_carrito.html', {
        'form': form,
        'items': items,
        'total': sum(item['subtotal'] for item in items)
    })