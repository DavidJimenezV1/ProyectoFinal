from django.apps import AppConfig


class AuditoriasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auditorias'
    verbose_name = 'Sistema de Auditoría'
    
    def ready(self):
        """Importar signals cuando la app esté lista"""
        import auditorias.signals
