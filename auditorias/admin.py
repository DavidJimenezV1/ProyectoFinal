from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from auditorias.models import (
    AuditLog, HistorialProducto, HistorialPedido, 
    HistorialCotizacion, HistorialFactura, HistorialCliente, HistorialCategoria
)


class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('get_accion_badge', 'usuario', 'modelo', 'objeto_nombre', 'timestamp_formateado', 'ip_address')
    list_filter = ('accion', 'modelo', 'timestamp', 'usuario')
    search_fields = ('usuario__username', 'modelo', 'objeto_nombre', 'descripcion')
    readonly_fields = ('usuario', 'accion', 'timestamp', 'modelo', 'objeto_id', 
                      'datos_anteriores', 'datos_nuevos', 'ip_address', 'descripcion')
    
    fieldsets = (
        ('Información General', {
            'fields': ('usuario', 'accion', 'timestamp', 'ip_address')
        }),
        ('Objeto Modificado', {
            'fields': ('modelo', 'objeto_id', 'objeto_nombre')
        }),
        ('Cambios', {
            'fields': ('descripcion', 'datos_anteriores', 'datos_nuevos', 'cambios_resumidos'),
            'classes': ('collapse',)
        }),
    )
    
    def get_accion_badge(self, obj):
        """Mostrar acción con color de fondo"""
        colors = {
            'CREATE': '#28a745',  # verde
            'UPDATE': '#ffc107',  # amarillo
            'DELETE': '#dc3545',  # rojo
            'VIEW': '#17a2b8',    # azul
        }
        color = colors.get(obj.accion, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_accion_display()
        )
    get_accion_badge.short_description = 'Acción'
    
    def timestamp_formateado(self, obj):
        return obj.timestamp.strftime('%d/%m/%Y %H:%M:%S')
    timestamp_formateado.short_description = 'Fecha y Hora'
    
    def has_add_permission(self, request):
        """No se pueden crear auditorías manualmente"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Solo el superuser puede eliminar auditorías"""
        return request.user.is_superuser
    
    def get_queryset(self, request):
        """Filtrar por usuario si no es superuser"""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(usuario=request.user)
        return qs


class HistorialProductoAdmin(admin.ModelAdmin):
    list_display = ('producto_id', 'get_accion', 'precio_anterior', 'precio_nuevo', 'stock_anterior', 'stock_nuevo', 'timestamp')
    list_filter = ('audit_log__accion', 'audit_log__timestamp')
    search_fields = ('producto_id',)
    readonly_fields = ('audit_log', 'producto_id', 'precio_anterior', 'precio_nuevo', 'stock_anterior', 'stock_nuevo', 'estado_anterior', 'estado_nuevo')
    
    def get_accion(self, obj):
        return obj.audit_log.get_accion_display()
    get_accion.short_description = 'Acción'
    
    def timestamp(self, obj):
        return obj.audit_log.timestamp.strftime('%d/%m/%Y %H:%M:%S')
    timestamp.short_description = 'Fecha y Hora'
    
    def has_add_permission(self, request):
        return False


class HistorialPedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido_id', 'get_accion', 'estado_anterior', 'estado_nuevo', 'total_anterior', 'total_nuevo', 'timestamp')
    list_filter = ('audit_log__accion', 'audit_log__timestamp')
    search_fields = ('pedido_id',)
    readonly_fields = ('audit_log', 'pedido_id', 'estado_anterior', 'estado_nuevo', 'total_anterior', 'total_nuevo', 'cliente_anterior', 'cliente_nuevo')
    
    def get_accion(self, obj):
        return obj.audit_log.get_accion_display()
    get_accion.short_description = 'Acción'
    
    def timestamp(self, obj):
        return obj.audit_log.timestamp.strftime('%d/%m/%Y %H:%M:%S')
    timestamp.short_description = 'Fecha y Hora'
    
    def has_add_permission(self, request):
        return False


class HistorialCotizacionAdmin(admin.ModelAdmin):
    list_display = ('cotizacion_id', 'get_accion', 'estado_anterior', 'estado_nuevo', 'monto_anterior', 'monto_nuevo', 'timestamp')
    list_filter = ('audit_log__accion', 'audit_log__timestamp')
    search_fields = ('cotizacion_id',)
    readonly_fields = ('audit_log', 'cotizacion_id', 'estado_anterior', 'estado_nuevo', 'monto_anterior', 'monto_nuevo')
    
    def get_accion(self, obj):
        return obj.audit_log.get_accion_display()
    get_accion.short_description = 'Acción'
    
    def timestamp(self, obj):
        return obj.audit_log.timestamp.strftime('%d/%m/%Y %H:%M:%S')
    timestamp.short_description = 'Fecha y Hora'
    
    def has_add_permission(self, request):
        return False


class HistorialFacturaAdmin(admin.ModelAdmin):
    list_display = ('factura_id', 'get_accion', 'estado_anterior', 'estado_nuevo', 'monto_anterior', 'monto_nuevo', 'timestamp')
    list_filter = ('audit_log__accion', 'audit_log__timestamp')
    search_fields = ('factura_id',)
    readonly_fields = ('audit_log', 'factura_id', 'monto_anterior', 'monto_nuevo', 'estado_anterior', 'estado_nuevo')
    
    def get_accion(self, obj):
        return obj.audit_log.get_accion_display()
    get_accion.short_description = 'Acción'
    
    def timestamp(self, obj):
        return obj.audit_log.timestamp.strftime('%d/%m/%Y %H:%M:%S')
    timestamp.short_description = 'Fecha y Hora'
    
    def has_add_permission(self, request):
        return False


class HistorialClienteAdmin(admin.ModelAdmin):
    list_display = ('cliente_id', 'get_accion', 'timestamp')
    list_filter = ('audit_log__accion', 'audit_log__timestamp')
    search_fields = ('cliente_id',)
    readonly_fields = ('audit_log', 'cliente_id', 'cambios')
    
    def get_accion(self, obj):
        return obj.audit_log.get_accion_display()
    get_accion.short_description = 'Acción'
    
    def timestamp(self, obj):
        return obj.audit_log.timestamp.strftime('%d/%m/%Y %H:%M:%S')
    timestamp.short_description = 'Fecha y Hora'
    
    def has_add_permission(self, request):
        return False


class HistorialCategoriaAdmin(admin.ModelAdmin):
    list_display = ('categoria_id', 'get_accion', 'nombre_anterior', 'nombre_nuevo', 'timestamp')
    list_filter = ('audit_log__accion', 'audit_log__timestamp')
    search_fields = ('categoria_id',)
    readonly_fields = ('audit_log', 'categoria_id', 'nombre_anterior', 'nombre_nuevo', 'descripcion_anterior', 'descripcion_nueva')
    
    def get_accion(self, obj):
        return obj.audit_log.get_accion_display()
    get_accion.short_description = 'Acción'
    
    def timestamp(self, obj):
        return obj.audit_log.timestamp.strftime('%d/%m/%Y %H:%M:%S')
    timestamp.short_description = 'Fecha y Hora'
    
    def has_add_permission(self, request):
        return False


# Registrar todos los modelos
admin.site.register(AuditLog, AuditLogAdmin)
admin.site.register(HistorialProducto, HistorialProductoAdmin)
admin.site.register(HistorialPedido, HistorialPedidoAdmin)
admin.site.register(HistorialCotizacion, HistorialCotizacionAdmin)
admin.site.register(HistorialFactura, HistorialFacturaAdmin)
admin.site.register(HistorialCliente, HistorialClienteAdmin)
admin.site.register(HistorialCategoria, HistorialCategoriaAdmin)