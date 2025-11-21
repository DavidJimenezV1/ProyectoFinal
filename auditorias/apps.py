from django.apps import AppConfig


class AuditoriasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auditorias'
    verbose_name = 'Sistema de Auditorías'
    
    def ready(self):
        """Conectar signals cuando la app esté lista"""
        from . import apps_signals
