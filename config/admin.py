from django.contrib.admin import AdminSite

class CustomAdminSite(AdminSite):
    """Sitio de administración personalizado para Tejos Olímpica"""
    site_header = "🏆 Tejos Olímpica - Administración"
    site_title = "Panel Admin"
    index_title = "📊 Panel de Control"
    
    # Personalización adicional
    enable_nav_sidebar = True  # Habilita la barra lateral de navegación
    
    def index(self, request, extra_context=None):
        """Personalización del índice del admin"""
        extra_context = extra_context or {}
        extra_context['site_header'] = "🏆 Tejos Olímpica - Administración"
        return super().index(request, extra_context)


# Instancia global del sitio personalizado
admin_site = CustomAdminSite(name='admin')