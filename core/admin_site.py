from django.contrib.admin import AdminSite
from django.urls import reverse
from django.utils.html import format_html
from django. template.response import TemplateResponse
from .views import get_admin_stats


class CustomAdminSite(AdminSite):
    """
    Sitio de administración personalizado con estadísticas en el dashboard. 
    """
    site_header = "🏆 Tejos Olímpica - Administración"
    site_title = "Admin Tejos Olímpica"
    index_title = "Panel de Control"

    def index(self, request, extra_context=None):
        """
        Personalizar la página de índice del admin con estadísticas.
        """
        # Obtener estadísticas REALES de la base de datos
        stats = get_admin_stats()

        print(f"✅ DEBUG - Stats obtenidas en admin_site.py: {stats}")

        # Contexto personalizado con TODOS los datos
        extra_context = extra_context or {}
        extra_context.update({
            # Productos
            'total_productos': stats.get('total_productos', 0),
            'productos_sin_stock': stats.get('productos_sin_stock', 0),
            
            # Pedidos
            'pedidos_pendientes': stats.get('pedidos_pendientes', 0),
            'pedidos_en_proceso': stats.get('pedidos_en_proceso', 0),
            'pedidos_completados': stats.get('pedidos_completados', 0),
            'total_pedidos': stats.get('total_pedidos', 0),
            
            # Clientes
            'total_clientes': stats.get('total_clientes', 0),
            'total_usuarios': stats.get('total_usuarios', 0),
            
            # Ingresos
            'ingresos_totales': stats.get('ingresos_totales', 0),
            'total_ventas': stats.get('total_ventas', 0),
            
            # Categorías
            'total_categorias': stats.get('total_categorias', 0),
            
            # Cotizaciones
            'cotizaciones_pendientes': stats.get('cotizaciones_pendientes', 0),
            'total_cotizaciones': stats.get('total_cotizaciones', 0),
            
            # Metadata del sitio
            'site_header': self.site_header,
            'site_title': self. site_title,
            'title': self.index_title,
        })

        print(f"✅ DEBUG - Extra context: {extra_context}")

        return TemplateResponse(
            request,
            self.index_template or 'admin/index.html',
            extra_context,
        )


# Crear instancia personalizada
custom_admin_site = CustomAdminSite(name='custom_admin')