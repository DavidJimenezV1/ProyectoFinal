from django.apps import AppConfig


class VentasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ventas'

    def ready(self):
        """Se ejecuta cuando Django carga la app"""
        from config.admin import admin_site
        from .models import Factura, ItemFactura
        from .admin import FacturaAdmin, ItemFacturaAdmin
        
        # Registrar en el sitio personalizado
        if not admin_site._registry.get(Factura):
            admin_site.register(Factura, FacturaAdmin)
        if not admin_site._registry.get(ItemFactura):
            admin_site.register(ItemFactura, ItemFacturaAdmin)