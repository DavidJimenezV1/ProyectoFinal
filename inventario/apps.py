from django.apps import AppConfig


class InventarioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventario'

    def ready(self):
        """Se ejecuta cuando Django carga la app"""
        from config.admin import admin_site
        from .models import Categoria, Producto, ImagenProducto
        from .admin import ProductoAdmin, ImagenProductoAdmin, CategoriaAdmin
        
        # Registrar en el sitio personalizado
        if not admin_site._registry.get(Producto):
            admin_site.register(Producto, ProductoAdmin)
        if not admin_site._registry.get(ImagenProducto):
            admin_site.register(ImagenProducto, ImagenProductoAdmin)
        if not admin_site._registry.get(Categoria):
            admin_site.register(Categoria, CategoriaAdmin)