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
from cotizaciones.models import Cotizacion
from ventas.models import Factura
from django.contrib.admin.views.decorators import staff_member_required

class HomePage(TemplateView):
    """
    Vista para la página de inicio pública.
    Muestra información general de la empresa y productos destacados.
    """
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener productos destacados
        context['productos_destacados'] = Producto.objects.all().order_by('?')[:4]
        
        # Obtener categorías principales
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
        
        context['total_productos'] = Producto.objects.count()
        context['total_clientes'] = Usuario.objects.filter(tipo_usuario='cliente').count()
        context['productos_sin_stock'] = Producto.objects.filter(stock=0).count()
        context['pedidos_recientes'] = Pedido.objects.all().order_by('-fecha_pedido')[:5]
        
        return context

def dashboard_stats(request):
    """API para obtener estadísticas del dashboard."""
    if not request.user.is_authenticated or not request.user.es_admin:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    dias = int(request.GET.get('dias', 30))
    fecha_inicio = timezone.now() - timedelta(days=dias)
    
    pedidos = Pedido.objects.filter(fecha_creacion__gte=fecha_inicio)
    
    pedidos_por_dia = list(pedidos.extra(
        select={'dia': "DATE(fecha_creacion)"}
    ).values('dia').annotate(
        total=Count('id')
    ).order_by('dia'))
    
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

# ========== ESTADÍSTICAS PARA ADMIN ==========

def get_admin_stats():
    """
    Obtiene estadísticas REALES de la base de datos para el admin dashboard.
    """
    try:
        stats = {
            # Productos
            'total_productos': Producto.objects.count(),
            'productos_sin_stock': Producto.objects.filter(stock=0).count(),
            
            # Pedidos
            'total_pedidos': Pedido.objects.count(),
            'pedidos_pendientes': Pedido.objects.filter(estado='pendiente').count(),
            'pedidos_en_proceso': Pedido.objects.filter(estado='en_proceso').count(),
            'pedidos_completados': Pedido.objects.filter(estado='completada').count(),
            
            # Clientes
            'total_clientes': Usuario.objects.filter(tipo_usuario='cliente').count(),
            'total_usuarios': Usuario.objects.count(),
            
            # Facturas e Ingresos
            'total_ventas': Factura.objects.count(),
            'ingresos_totales': Pedido.objects.aggregate(Sum('total'))['total__sum'] or 0,
            
            # Categorías
            'total_categorias': Categoria.objects.count(),
            
            # Cotizaciones
            'cotizaciones_pendientes': Cotizacion.objects.filter(estado='pendiente').count(),
            'total_cotizaciones': Cotizacion.objects.count(),
        }
        return stats
    
    except Exception as e:
        print(f"Error al obtener estadísticas: {e}")
        return {
            'total_productos': 0,
            'productos_sin_stock': 0,
            'total_pedidos': 0,
            'pedidos_pendientes': 0,
            'pedidos_en_proceso': 0,
            'pedidos_completados': 0,
            'total_clientes': 0,
            'total_usuarios': 0,
            'total_ventas': 0,
            'ingresos_totales': 0,
            'total_categorias': 0,
            'cotizaciones_pendientes': 0,
            'total_cotizaciones': 0,
        }

@staff_member_required
def admin_dashboard(request):
    """Vista personalizada del dashboard administrativo"""
    
    hoy = timezone.now()
    hace_un_mes = hoy - timedelta(days=30)
    
    try:
        total_sales = Pedido.objects.filter(
            fecha_creacion__gte=hace_un_mes
        ).aggregate(Sum('total'))['total__sum'] or 0
        
        pending_orders = Pedido.objects.filter(estado='pendiente').count()
        
        total_inventory = Producto.objects.aggregate(
            Sum('stock')
        )['stock__sum'] or 0
        
        active_customers = Usuario.objects.filter(tipo_usuario='cliente').count()
        
        total_revenue = Pedido.objects.filter(
            fecha_creacion__gte=hace_un_mes
        ).aggregate(Sum('total'))['total__sum'] or 0
        
        total_orders = Pedido.objects.filter(
            fecha_creacion__gte=hace_un_mes
        ).count()
        completed_orders = Pedido.objects.filter(
            estado='completada',
            fecha_creacion__gte=hace_un_mes
        ).count()
        conversion_rate = round(
            (completed_orders / total_orders * 100) if total_orders > 0 else 0, 2
        )
        
        orders_pending = Pedido.objects.filter(estado='pendiente').count()
        orders_in_process = Pedido.objects.filter(estado='en_proceso').count()
        orders_completed = Pedido.objects.filter(estado='completada').count()
        orders_cancelled = Pedido.objects.filter(estado='cancelada').count()
        
        context = {
            'total_sales': int(total_sales),
            'pending_orders': pending_orders,
            'total_inventory': total_inventory,
            'active_customers': active_customers,
            'total_revenue': int(total_revenue),
            'conversion_rate': conversion_rate,
            'orders_pending': orders_pending,
            'orders_in_process': orders_in_process,
            'orders_completed': orders_completed,
            'orders_cancelled': orders_cancelled,
        }
    
    except Exception as e:
        print(f"Error en admin_dashboard: {e}")
        context = {
            'total_sales': 0,
            'pending_orders': 0,
            'total_inventory': 0,
            'active_customers': 0,
            'total_revenue': 0,
            'conversion_rate': 0,
            'orders_pending': 0,
            'orders_in_process': 0,
            'orders_completed': 0,
            'orders_cancelled': 0,
        }
    
    return render(request, 'admin_custom/dashboard_enhanced.html', context)