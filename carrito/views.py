from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from inventario.models import Producto
from decimal import Decimal

def ver_carrito(request):
    """Ver el contenido del carrito con los cálculos de precio"""
    carrito = request.session.get('carrito', {})
    items = []
    total = Decimal('0.00')
    
    # Convertir IDs a objetos de producto con sus precios
    for producto_id, cantidad in carrito.items():
        try:
            producto = Producto.objects.get(id=producto_id)
            subtotal = producto.precio * Decimal(str(cantidad))
            total += subtotal
            
            items.append({
                'producto': producto,
                'cantidad': cantidad,
                'precio_unitario': producto.precio,
                'subtotal': subtotal
            })
        except Producto.DoesNotExist:
            pass
            
    return render(request, 'carrito/carrito.html', {
        'items': items,
        'total_items': sum(item['cantidad'] for item in items),
        'total': total
    })

def agregar_producto(request, producto_id):
    """Mostrar formulario para seleccionar cantidad antes de agregar al carrito"""
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        # El usuario envió la cantidad
        cantidad = int(request.POST.get('cantidad', 1))
        
        if cantidad <= 0:
            messages.error(request, 'La cantidad debe ser mayor a 0')
            return redirect('carrito:agregar', producto_id=producto_id)
        
        # Agregar al carrito
        carrito = request.session.get('carrito', {})
        producto_id_str = str(producto_id)
        
        if producto_id_str in carrito:
            carrito[producto_id_str] += cantidad
        else:
            carrito[producto_id_str] = cantidad
        
        request.session['carrito'] = carrito
        messages.success(request, f'{producto.nombre} x{cantidad} añadido al carrito')
        
        # Redirigir de vuelta a donde vino
        next_url = request.POST.get('next', request.GET.get('next', 'catalogo:lista_productos'))
        return redirect(next_url)
    
    # GET: Mostrar formulario pidiendo cantidad
    next_url = request.GET.get('next', 'catalogo:lista_productos')
    return render(request, 'carrito/seleccionar_cantidad.html', {
        'producto': producto,
        'next': next_url
    })

def eliminar_producto(request, producto_id):
    """Eliminar un producto del carrito"""
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = request.session.get('carrito', {})
    producto_id = str(producto_id)
    
    if producto_id in carrito:
        del carrito[producto_id]
        request.session['carrito'] = carrito
        messages.success(request, f'{producto.nombre} eliminado del carrito')
    
    return redirect('carrito:ver_carrito')

def actualizar_cantidad(request, producto_id):
    """Actualizar la cantidad de un producto en el carrito"""
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        carrito = request.session.get('carrito', {})
        producto_id = str(producto_id)
        
        if cantidad > 0:
            carrito[producto_id] = cantidad
        else:
            del carrito[producto_id]
            
        request.session['carrito'] = carrito
    
    return redirect('carrito:ver_carrito')

def vaciar_carrito(request):
    """Vaciar el carrito completamente"""
    request.session['carrito'] = {}
    messages.success(request, 'Carrito de cotización vacío')
    return redirect('carrito:ver_carrito')

def convertir_a_cotizacion(request):
    """Convertir el carrito en una cotización formal"""
    # Si no está autenticado, redirigir al login con mensaje
    if not request.user.is_authenticated:
        messages.info(request, 'Debes iniciar sesión para solicitar una cotización formal')
        return redirect('login')
    
    # Si el carrito está vacío, redirigir al catálogo
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.warning(request, 'Tu carrito de cotización está vacío')
        return redirect('catalogo:lista_productos')
    
    # Redirigir al formulario de cotización con los productos del carrito
    return redirect('cotizaciones:nueva_cotizacion_desde_carrito')
