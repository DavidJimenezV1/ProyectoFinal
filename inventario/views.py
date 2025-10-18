from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Producto, Categoria
from django.http import JsonResponse
from django.views.decorators.http import require_GET

# Si tienes vistas existentes, mantenlas aquí...
# Ejemplo: vistas para listar productos, mostrar detalles, etc.

class ProductoListView(ListView):
    model = Producto
    template_name = 'inventario/producto_list.html'
    context_object_name = 'productos'

class ProductoDetailView(DetailView):
    model = Producto
    template_name = 'inventario/producto_detail.html'
    context_object_name = 'producto'

# Aquí agregamos la nueva función API
@require_GET
def obtener_precio_producto(request, producto_id):
    """API simple para obtener el precio de un producto"""
    try:
        producto = Producto.objects.get(pk=producto_id)
        return JsonResponse({'precio': float(producto.precio)})
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)