from django.views.generic import ListView, DetailView
from django.shortcuts import render, redirect
from django.db.models import Q
from inventario.models import Producto, Categoria, ImagenProducto

class ProductoListView(ListView):
    """
    Vista para mostrar el catálogo de productos.
    Permite filtrar por categoría y términos de búsqueda.
    """
    model = Producto
    template_name = 'catalogo/lista_productos.html'
    context_object_name = 'productos'
    paginate_by = 12  # Productos por página
    
    def get_queryset(self):
        """Personaliza la consulta para permitir filtros"""
        queryset = Producto.objects.all().order_by('id')
        
        # Filtrar por categoría
        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
            
        # Filtrar por término de búsqueda
        buscar = self.request.GET.get('buscar')
        if buscar:
            queryset = queryset.filter(
                Q(nombre__icontains=buscar) |
                Q(descripcion__icontains=buscar) |
                Q(codigo__icontains=buscar)
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        """Añade datos adicionales al contexto"""
        context = super().get_context_data(**kwargs)
        
        # Obtener todas las categorías para el menú de filtros
        context['categorias'] = Categoria.objects.all()
        
        # Mantener el término de búsqueda para la paginación
        if 'buscar' in self.request.GET:
            context['buscar'] = self.request.GET.get('buscar')
            
        # Mantener la categoría seleccionada
        if 'categoria' in self.request.GET:
            context['categoria_seleccionada'] = int(self.request.GET.get('categoria'))
        
        return context


class ProductoDetailView(DetailView):
    """
    Vista para mostrar los detalles de un producto específico.
    Incluye todas sus imágenes y detalles.
    """
    model = Producto
    template_name = 'catalogo/detalle_producto.html'
    context_object_name = 'producto'
    
    def get_context_data(self, **kwargs):
        """Añade datos adicionales al contexto"""
        context = super().get_context_data(**kwargs)
        
        # Productos relacionados (de la misma categoría)
        context['productos_relacionados'] = Producto.objects.filter(
            categoria=self.object.categoria
        ).exclude(id=self.object.id)[:4]  # Mostrar máximo 4 productos relacionados
        
        return context


def filtrar_productos(request):
    """
    Vista funcional para filtrar productos por categoría.
    Redirige a la vista de lista con los parámetros apropiados.
    """
    categoria_id = request.GET.get('categoria')
    buscar = request.GET.get('buscar', '')
    
    url = '/catalogo/'
    params = []
    
    if categoria_id:
        params.append(f'categoria={categoria_id}')
    
    if buscar:
        params.append(f'buscar={buscar}')
    
    if params:
        url += '?' + '&'.join(params)
    
    return redirect(url)