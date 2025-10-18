from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from inventario.models import Producto, Categoria
from pedidos.models import Pedido
from usuarios.models import Usuario

class HomePage(TemplateView):
    """
    Vista para la página de inicio pública.
    Muestra información general de la empresa y productos destacados.
    """
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener productos destacados - CORREGIDO: Sin filtro "activo"
        context['productos_destacados'] = Producto.objects.all().order_by('?')[:4]
        
        # Obtener categorías principales para mostrar en la página inicial
        context['categorias'] = Categoria.objects.annotate(
            num_productos=Count('producto')
        ).filter(num_productos__gt=0)[:3]
        
        return context

class AdminDashboard(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Vista para el dashboard administrativo.
    Requiere inicio de sesión y permisos de administrador.
    """
    template_name = 'core/dashboard.html'
    login_url = '/usuarios/login/'
    
    def test_func(self):
        """Verificar que el usuario sea administrador"""
        return self.request.user.es_admin
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas básicas para el dashboard
        context['total_productos'] = Producto.objects.count()
        context['total_clientes'] = Usuario.objects.filter(tipo_usuario='cliente').count()
        context['productos_sin_stock'] = Producto.objects.filter(stock=0).count()
        
        # Pedidos recientes
        context['pedidos_recientes'] = Pedido.objects.all().order_by('-fecha_creacion')[:5]
        
        return context

def dashboard_stats(request):
    """
    API para obtener estadísticas del dashboard.
    Utilizado para gráficas y widgets dinámicos.
    """
    # Verificar que el usuario tenga permisos
    if not request.user.is_authenticated or not request.user.es_admin:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    # Período de tiempo (últimos 30 días por defecto)
    dias = int(request.GET.get('dias', 30))
    fecha_inicio = timezone.now() - timedelta(days=dias)
    
    # Estadísticas de pedidos
    pedidos = Pedido.objects.filter(fecha_creacion__gte=fecha_inicio)
    
    # Datos para gráficas
    pedidos_por_dia = list(pedidos.extra(
        select={'dia': "DATE(fecha_creacion)"}
    ).values('dia').annotate(
        total=Count('id')
    ).order_by('dia'))
    
    # Top productos
    top_productos = Producto.objects.filter(
        detallepedido__pedido__fecha_creacion__gte=fecha_inicio
    ).annotate(
        total_vendido=Sum('detallepedido__cantidad')
    ).order_by('-total_vendido')[:5]
    
    top_productos_data = [{
        'nombre': p.nombre,
        'cantidad': p.total_vendido or 0
    } for p in top_productos]
    
    return JsonResponse({
        'pedidos_por_dia': pedidos_por_dia,
        'top_productos': top_productos_data,
        'total_pedidos': pedidos.count(),
        'valor_promedio': pedidos.aggregate(avg=Avg('total'))['avg'] or 0
    })

def error_404(request, exception):
    """Vista personalizada para errores 404"""
    return render(request, 'core/404.html', status=404)

def error_500(request):
    """Vista personalizada para errores 500"""
    return render(request, 'core/500.html', status=500)