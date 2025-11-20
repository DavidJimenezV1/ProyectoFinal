from django.apps import AppConfig

class VentasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ventas'
    verbose_name = 'Facturación y Ventas'

    def ready(self):
        import ventas.signals  # Importar las señales