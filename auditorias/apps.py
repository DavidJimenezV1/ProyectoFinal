from django.apps import AppConfig

class AuditoriasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auditorias'
    verbose_name = 'Auditorías y Historial'

    def ready(self):
        import auditorias.signals