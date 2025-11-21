from django.apps import AppConfig


class CotizacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cotizaciones'
    
    def ready(self):
        """Se ejecuta cuando la app se carga - registra los signals"""
        import auditorias.apps_signals