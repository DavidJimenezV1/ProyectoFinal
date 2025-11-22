from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Producto, Categoria
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

# ==================== VISTAS EXISTENTES ====================

class ProductoListView(ListView):
    model = Producto
    template_name = 'inventario/producto_list.html'
    context_object_name = 'productos'

class ProductoDetailView(DetailView):
    model = Producto
    template_name = 'inventario/producto_detail.html'
    context_object_name = 'producto'

# ==================== API - OBTENER PRECIO PRODUCTO ====================

@require_http_methods(["GET"])
def obtener_precio_producto(request, producto_id):
    """API simple para obtener el precio de un producto"""
    try:
        producto = Producto.objects.get(pk=producto_id)
        return JsonResponse({
            'precio': float(producto.precio),
            'stock': producto.stock
        })
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)

# ==================== API - OBTENER PRECIO Y STOCK (ALIAS) ====================

@require_http_methods(["GET"])
def get_producto_precio(request, producto_id):
    """API para obtener el precio y stock de un producto"""
    try:
        producto = Producto.objects.get(id=producto_id)
        return JsonResponse({
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': str(producto.precio),
            'stock': producto.stock
        })
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)