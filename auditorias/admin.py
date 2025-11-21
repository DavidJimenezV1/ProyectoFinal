from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from django.db.models import Q, Count
from datetime import timedelta, datetime
from django.utils import timezone
import csv

from .models import (
    AuditLog,
    HistorialProducto,
    HistorialPedido,
    HistorialCotizacion,
    HistorialFactura,
    HistorialCliente,
    HistorialCategoria
)


# Filtros personalizados
class FechaRangoFilter(admin.SimpleListFilter):
    """Filtro personalizado por rangos de fecha"""
    title = 'Rango de fecha'
    parameter_name = 'fecha_rango'
    
    def lookups(self, request, model_admin):
        return (
            ('hoy', 'Hoy'),
            ('ayer', 'Ayer'),
            ('ultima_semana', 'Última semana'),
            ('ultimo_mes', 'Último mes'),
            ('ultimo_trimestre', 'Último trimestre'),
            ('ultimo_ano', 'Último año'),
        )
    
    def queryset(self, request, queryset):
        now = timezone.now()
        
        if self.value() == 'hoy':
            return queryset.filter(fecha_hora__date=now.date())
        elif self.value() == 'ayer':
            ayer = now - timedelta(days=1)
            return queryset.filter(fecha_hora__date=ayer.date())
        elif self.value() == 'ultima_semana':
            inicio = now - timedelta(days=7)
            return queryset.filter(fecha_hora__gte=inicio)
        elif self.value() == 'ultimo_mes':
            inicio = now - timedelta(days=30)
            return queryset.filter(fecha_hora__gte=inicio)
        elif self.value() == 'ultimo_trimestre':
            inicio = now - timedelta(days=90)
            return queryset.filter(fecha_hora__gte=inicio)
        elif self.value() == 'ultimo_ano':
            inicio = now - timedelta(days=365)
            return queryset.filter(fecha_hora__gte=inicio)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin mejorado para el registro de auditoría general"""
    
    list_display = [
        'id',
        'fecha_hora_formateada',
        'usuario_display',
        'accion_badge',
        'modelo',
        'objeto_repr',
        'ver_cambios_btn'
    ]
    
    list_filter = [
        'accion',
        FechaRangoFilter,
        'modelo',
        'usuario',
    ]
    
    search_fields = [
        'usuario_nombre',
        'modelo',
        'objeto_repr',
        'notas'
    ]
    
    date_hierarchy = 'fecha_hora'
    
    readonly_fields = [
        'usuario',
        'usuario_nombre',
        'accion',
        'fecha_hora',
        'content_type',
        'object_id',
        'modelo',
        'objeto_repr',
        'cambios_display',
        'ip_address',
        'user_agent'
    ]
    
    fieldsets = (
        ('Información General', {
            'fields': ('fecha_hora', 'usuario', 'usuario_nombre', 'accion')
        }),
        ('Objeto Afectado', {
            'fields': ('content_type', 'object_id', 'modelo', 'objeto_repr')
        }),
        ('Detalles de Cambios', {
            'fields': ('cambios_display',),
            'classes': ('wide',)
        }),
        ('Información Técnica', {
            'fields': ('ip_address', 'user_agent', 'notas'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['exportar_csv', 'exportar_excel']
    
    def get_queryset(self, request):
        """Filtrar registros según permisos del usuario"""
        qs = super().get_queryset(request)
        
        # Si el usuario es superusuario o Admin Mayor, ver todo
        if request.user.is_superuser:
            return qs
        
        # Si es admin pero no superusuario, solo ver sus propios registros
        if hasattr(request.user, 'tipo_usuario') and request.user.tipo_usuario == 'admin':
            return qs
        
        # Usuarios normales solo ven sus propios registros
        return qs.filter(usuario=request.user)
    
    def has_add_permission(self, request):
        """No permitir crear registros de auditoría manualmente"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Solo superusuarios pueden eliminar registros de auditoría"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """No permitir editar registros de auditoría"""
        return False
    
    def fecha_hora_formateada(self, obj):
        """Muestra la fecha y hora formateada"""
        return obj.fecha_hora.strftime('%d/%m/%Y %H:%M:%S')
    fecha_hora_formateada.short_description = 'Fecha y Hora'
    fecha_hora_formateada.admin_order_field = 'fecha_hora'
    
    def usuario_display(self, obj):
        """Muestra el usuario con badge"""
        if obj.usuario:
            return format_html(
                '<span style="background-color: #417690; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
                obj.usuario_nombre
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 3px 8px; border-radius: 3px;">Sistema</span>'
        )
    usuario_display.short_description = 'Usuario'
    
    def accion_badge(self, obj):
        """Muestra la acción con colores distintivos"""
        colors = {
            'CREATE': '#28a745',  # Verde
            'UPDATE': '#ffc107',  # Amarillo
            'DELETE': '#dc3545',  # Rojo
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold;">{}</span>',
            colors.get(obj.accion, '#6c757d'),
            obj.get_accion_display()
        )
    accion_badge.short_description = 'Acción'
    accion_badge.admin_order_field = 'accion'
    
    def ver_cambios_btn(self, obj):
        """Botón para ver cambios en modal"""
        if obj.cambios:
            # Usar escape seguro para JavaScript
            from django.utils.html import escapejs
            cambios_escapados = escapejs(obj.cambios_formateados)
            return format_html(
                '<button type="button" onclick="alert(\'{}\');" style="background-color: #17a2b8; color: white; padding: 4px 8px; border-radius: 3px; border: none; cursor: pointer;">👁️ Ver</button>',
                cambios_escapados
            )
        return '-'
    ver_cambios_btn.short_description = 'Cambios'
    
    def cambios_display(self, obj):
        """Muestra los cambios en formato legible"""
        if not obj.cambios:
            return mark_safe('<i>Sin cambios registrados</i>')
        
        html = '<div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px;">'
        html += '<pre style="margin: 0;">'
        html += obj.cambios_formateados
        html += '</pre></div>'
        return mark_safe(html)
    cambios_display.short_description = 'Cambios Realizados'
    
    def exportar_csv(self, request, queryset):
        """Exportar registros seleccionados a CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="auditoria_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Fecha', 'Usuario', 'Acción', 'Modelo', 'Objeto', 'Cambios'])
        
        for obj in queryset:
            writer.writerow([
                obj.fecha_hora.strftime('%Y-%m-%d %H:%M:%S'),
                obj.usuario_nombre,
                obj.get_accion_display(),
                obj.modelo,
                obj.objeto_repr,
                obj.cambios_formateados
            ])
        
        return response
    exportar_csv.short_description = '📥 Exportar a CSV'
    
    def exportar_excel(self, request, queryset):
        """Exportar registros seleccionados a Excel (CSV compatible)"""
        return self.exportar_csv(request, queryset)
    exportar_excel.short_description = '📊 Exportar a Excel'


# Admin para historiales específicos
class HistorialBaseAdmin(admin.ModelAdmin):
    """Clase base para admins de historial"""
    date_hierarchy = 'fecha_hora'
    readonly_fields = ['fecha_hora', 'usuario', 'descripcion']
    
    list_filter = [FechaRangoFilter, 'usuario']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(HistorialProducto)
class HistorialProductoAdmin(HistorialBaseAdmin):
    list_display = ['fecha_hora', 'producto', 'usuario', 'precio_cambio', 'stock_cambio', 'descripcion']
    search_fields = ['producto__nombre', 'producto__codigo', 'descripcion']
    list_filter = HistorialBaseAdmin.list_filter + ['producto__categoria']
    
    readonly_fields = HistorialBaseAdmin.readonly_fields + [
        'producto',
        'nombre_anterior', 'nombre_nuevo',
        'precio_anterior', 'precio_nuevo',
        'stock_anterior', 'stock_nuevo'
    ]
    
    def precio_cambio(self, obj):
        if obj.precio_anterior and obj.precio_nuevo:
            if obj.precio_anterior != obj.precio_nuevo:
                return format_html(
                    '${} → ${}',
                    obj.precio_anterior,
                    obj.precio_nuevo
                )
        return '-'
    precio_cambio.short_description = 'Cambio de Precio'
    
    def stock_cambio(self, obj):
        if obj.stock_anterior is not None and obj.stock_nuevo is not None:
            if obj.stock_anterior != obj.stock_nuevo:
                diff = obj.stock_nuevo - obj.stock_anterior
                color = 'green' if diff > 0 else 'red'
                return format_html(
                    '<span style="color: {};">{} → {} ({})</span>',
                    color,
                    obj.stock_anterior,
                    obj.stock_nuevo,
                    f'+{diff}' if diff > 0 else str(diff)
                )
        return '-'
    stock_cambio.short_description = 'Cambio de Stock'


@admin.register(HistorialPedido)
class HistorialPedidoAdmin(HistorialBaseAdmin):
    list_display = ['fecha_hora', 'pedido', 'usuario', 'estado_cambio', 'descripcion']
    search_fields = ['pedido__id', 'descripcion']
    list_filter = HistorialBaseAdmin.list_filter + ['estado_nuevo']
    
    readonly_fields = HistorialBaseAdmin.readonly_fields + [
        'pedido', 'estado_anterior', 'estado_nuevo'
    ]
    
    def estado_cambio(self, obj):
        if obj.estado_anterior and obj.estado_nuevo:
            return format_html('{} → {}', obj.estado_anterior, obj.estado_nuevo)
        return obj.estado_nuevo or '-'
    estado_cambio.short_description = 'Cambio de Estado'


@admin.register(HistorialCotizacion)
class HistorialCotizacionAdmin(HistorialBaseAdmin):
    list_display = ['fecha_hora', 'cotizacion', 'usuario', 'estado_cambio', 'total_cambio', 'descripcion']
    search_fields = ['cotizacion__id', 'descripcion']
    list_filter = HistorialBaseAdmin.list_filter + ['estado_nuevo']
    
    readonly_fields = HistorialBaseAdmin.readonly_fields + [
        'cotizacion', 'estado_anterior', 'estado_nuevo',
        'total_anterior', 'total_nuevo'
    ]
    
    def estado_cambio(self, obj):
        if obj.estado_anterior and obj.estado_nuevo:
            return format_html('{} → {}', obj.estado_anterior, obj.estado_nuevo)
        return obj.estado_nuevo or '-'
    estado_cambio.short_description = 'Estado'
    
    def total_cambio(self, obj):
        if obj.total_anterior and obj.total_nuevo:
            if obj.total_anterior != obj.total_nuevo:
                return format_html('${} → ${}', obj.total_anterior, obj.total_nuevo)
        return '-'
    total_cambio.short_description = 'Total'


@admin.register(HistorialFactura)
class HistorialFacturaAdmin(HistorialBaseAdmin):
    list_display = ['fecha_hora', 'factura', 'usuario', 'estado_cambio', 'total_cambio', 'descripcion']
    search_fields = ['factura__numero', 'descripcion']
    list_filter = HistorialBaseAdmin.list_filter + ['estado_nuevo']
    
    readonly_fields = HistorialBaseAdmin.readonly_fields + [
        'factura', 'estado_anterior', 'estado_nuevo',
        'total_anterior', 'total_nuevo'
    ]
    
    def estado_cambio(self, obj):
        if obj.estado_anterior and obj.estado_nuevo:
            return format_html('{} → {}', obj.estado_anterior, obj.estado_nuevo)
        return obj.estado_nuevo or '-'
    estado_cambio.short_description = 'Estado'
    
    def total_cambio(self, obj):
        if obj.total_anterior and obj.total_nuevo:
            if obj.total_anterior != obj.total_nuevo:
                return format_html('${} → ${}', obj.total_anterior, obj.total_nuevo)
        return '-'
    total_cambio.short_description = 'Total'


@admin.register(HistorialCliente)
class HistorialClienteAdmin(HistorialBaseAdmin):
    list_display = ['fecha_hora', 'cliente', 'usuario', 'descripcion']
    search_fields = ['cliente__nombre', 'cliente__apellido', 'descripcion']
    
    readonly_fields = HistorialBaseAdmin.readonly_fields + ['cliente', 'cambios']


@admin.register(HistorialCategoria)
class HistorialCategoriaAdmin(HistorialBaseAdmin):
    list_display = ['fecha_hora', 'categoria', 'usuario', 'nombre_cambio', 'descripcion']
    search_fields = ['categoria__nombre', 'descripcion']
    
    readonly_fields = HistorialBaseAdmin.readonly_fields + [
        'categoria', 'nombre_anterior', 'nombre_nuevo'
    ]
    
    def nombre_cambio(self, obj):
        if obj.nombre_anterior and obj.nombre_nuevo:
            return format_html('{} → {}', obj.nombre_anterior, obj.nombre_nuevo)
        return obj.nombre_nuevo or '-'
    nombre_cambio.short_description = 'Cambio de Nombre'
