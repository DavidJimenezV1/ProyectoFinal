from django.apps import AppConfig


class AuditoriasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auditorias'
    
    def ready(self):
        """Se ejecuta cuando la app se carga"""
        import auditorias.apps_signals  # Importar los signals