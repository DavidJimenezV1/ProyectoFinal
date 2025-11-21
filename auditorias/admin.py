from django.contrib import admin
from .models import Auditoria
from .filters import AuditoriaFechaFilter, AuditoriaAccionFilter, AuditoriaModeloFilter


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    """Administración del modelo de Auditoría"""
    
    list_display = [
        'id',
        'fecha_hora',
        'usuario',
        'accion',
        'content_type',
        'objeto_repr',
        'ip_address'
    ]
    
    list_filter = [
        AuditoriaFechaFilter,
        AuditoriaAccionFilter,
        AuditoriaModeloFilter,
        'usuario',
    ]
    
    search_fields = [
        'objeto_repr',
        'usuario__username',
        'usuario__email',
        'ip_address'
    ]
    
    readonly_fields = [
        'usuario',
        'accion',
        'content_type',
        'object_id',
        'objeto_repr',
        'cambios',
        'fecha_hora',
        'ip_address',
        'cambios_formateados_display'
    ]
    
    date_hierarchy = 'fecha_hora'
    
    ordering = ['-fecha_hora']
    
    # No permitir agregar, editar o eliminar auditorías desde el admin
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def cambios_formateados_display(self, obj):
        """Muestra los cambios de forma legible en el admin"""
        return obj.cambios_formateados()
    
    cambios_formateados_display.short_description = 'Cambios Detallados'
    
    fieldsets = (
        ('Información General', {
            'fields': ('fecha_hora', 'usuario', 'ip_address')
        }),
        ('Acción Realizada', {
            'fields': ('accion', 'content_type', 'object_id', 'objeto_repr')
        }),
        ('Detalles del Cambio', {
            'fields': ('cambios', 'cambios_formateados_display'),
            'classes': ('collapse',)
        }),
    )
