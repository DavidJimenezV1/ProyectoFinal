from django.apps import AppConfig


class AuditoriasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
<<<<<<< HEAD
    name = 'auditorias'
    
    def ready(self):
        """Se ejecuta cuando la app se carga"""
        import auditorias.apps_signals  # Importar los signals
=======
    name = 'auditorias'
>>>>>>> 2ccf0aabe78d0f7aa0a68ef0a71d1f968443289f
