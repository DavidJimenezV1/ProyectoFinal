from django.contrib import admin
from .views import get_admin_stats

class CustomAdminSite(admin.AdminSite):
    """
    Sitio de administración personalizado con datos reales
    """
    site_header = "🏆 Tejos Olímpica - Administración"
    site_title = "Panel Admin"
    index_title = "Panel de Control"
    
    def index(self, request, extra_context=None):
        """
        Reemplaza el índice del admin con datos reales de la BD
        """
        extra_context = extra_context or {}
        # Obtener estadísticas reales
        extra_context.update(get_admin_stats())
        return super().index(request, extra_context)

# Opcional: Reemplazar el admin site por defecto
# admin.site = CustomAdminSite(name='admin')