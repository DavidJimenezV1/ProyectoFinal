from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
from django.db.models import Sum, Count
from datetime import datetime
import csv
from .models import Cliente, Pedido, DetallePedido

class DetalleInline(admin.TabularInline):
    model = DetallePedido
    extra = 1
    autocomplete_fields = ['producto']
    fields = ['producto', 'cantidad', 'precio_unitario', 'subtotal_display']
    readonly_fields = ['subtotal_display']
    
    def subtotal_display(self, obj):
        """Muestra el subtotal del detalle"""
        if obj.pk:
            return format_html('${:,.2f}', obj.subtotal())
        return '-'
    subtotal_display.short_description = 'Subtotal'

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'email', 'telefono', 'total_pedidos', 'ultimo_pedido')
    search_fields = ('nombre', 'apellido', 'email', 'telefono')
    list_per_page = 25
    
    actions = ['exportar_csv']
    
    def nombre_completo(self, obj):
        """Muestra el nombre completo"""
        return f"{obj.nombre} {obj.apellido}"
    nombre_completo.short_description = 'Cliente'
    nombre_completo.admin_order_field = 'nombre'
    
    def total_pedidos(self, obj):
        """Muestra el total de pedidos del cliente"""
        count = obj.pedido_set.count()
        return format_html(
            '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 10px;">{} pedidos</span>',
            count
        )
    total_pedidos.short_description = 'Total Pedidos'
    
    def ultimo_pedido(self, obj):
        """Muestra la fecha del último pedido"""
        ultimo = obj.pedido_set.order_by('-fecha_pedido').first()
        if ultimo:
            return ultimo.fecha_pedido.strftime('%d/%m/%Y')
        return '-'
    ultimo_pedido.short_description = 'Último Pedido'
    
    def exportar_csv(self, request, queryset):
        """Exportar clientes a CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="clientes.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Nombre', 'Apellido', 'Email', 'Teléfono', 'Dirección'])
        
        for cliente in queryset:
            writer.writerow([
                cliente.nombre,
                cliente.apellido,
                cliente.email,
                cliente.telefono,
                cliente.direccion
            ])
        
        self.message_user(request, f'{queryset.count()} clientes exportados correctamente.')
        return response
    exportar_csv.short_description = '📥 Exportar a CSV'

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id_display', 'cliente', 'fecha_pedido', 'fecha_entrega', 'estado_badge', 'total_display', 'acciones')
    list_filter = ('estado', 'fecha_pedido', 'fecha_entrega')
    search_fields = ('id', 'cliente__nombre', 'cliente__apellido', 'cliente__email')
    date_hierarchy = 'fecha_pedido'
    inlines = [DetalleInline]
    autocomplete_fields = ['cliente']
    list_per_page = 25
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('cliente', 'fecha_pedido', 'fecha_entrega', 'estado')
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('wide',)
        }),
    )
    
    readonly_fields = ['fecha_pedido']
    
    actions = ['cambiar_a_en_proceso', 'cambiar_a_completado', 'cambiar_a_cancelado', 'exportar_csv']
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        qs = super().get_queryset(request)
        return qs.select_related('cliente').prefetch_related('detallepedido_set__producto')
    
    def id_display(self, obj):
        """Muestra el ID con formato"""
        return format_html('<strong>#{}</strong>', obj.id)
    id_display.short_description = 'ID'
    id_display.admin_order_field = 'id'
    
    def estado_badge(self, obj):
        """Muestra el estado con badge de colores"""
        colors = {
            'pendiente': '#ffc107',
            'en_proceso': '#17a2b8',
            'completado': '#28a745',
            'cancelado': '#dc3545',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 12px; border-radius: 15px; font-weight: bold;">{}</span>',
            colors.get(obj.estado, '#6c757d'),
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    estado_badge.admin_order_field = 'estado'
    
    def total_display(self, obj):
        """Muestra el total del pedido"""
        total = obj.get_total()
        return format_html(
            '<span style="font-size: 14px; font-weight: bold; color: #28a745;">${:,.2f}</span>',
            total
        )
    total_display.short_description = 'Total'
    
    def acciones(self, obj):
        """Botones de acciones rápidas"""
        return format_html(
            '<a class="button" href="/admin/pedidos/pedido/{}/change/" style="background-color: #417690; color: white; padding: 5px 10px; border-radius: 3px; text-decoration: none;">✏️ Editar</a>',
            obj.id
        )
    acciones.short_description = 'Acciones'
    
    # Acciones en lote
    def cambiar_a_en_proceso(self, request, queryset):
        """Cambia el estado de pedidos a 'en proceso'"""
        updated = queryset.update(estado='en_proceso')
        self.message_user(request, f'{updated} pedido(s) cambiados a "En proceso".')
    cambiar_a_en_proceso.short_description = '🔄 Cambiar a En Proceso'
    
    def cambiar_a_completado(self, request, queryset):
        """Cambia el estado de pedidos a 'completado'"""
        updated = queryset.update(estado='completado')
        self.message_user(request, f'{updated} pedido(s) marcados como "Completado".')
    cambiar_a_completado.short_description = '✅ Marcar como Completado'
    
    def cambiar_a_cancelado(self, request, queryset):
        """Cambia el estado de pedidos a 'cancelado'"""
        updated = queryset.update(estado='cancelado')
        self.message_user(request, f'{updated} pedido(s) marcados como "Cancelado".')
    cambiar_a_cancelado.short_description = '❌ Marcar como Cancelado'
    
    def exportar_csv(self, request, queryset):
        """Exportar pedidos a CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="pedidos.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Cliente', 'Fecha Pedido', 'Estado', 'Total'])
        
        for pedido in queryset:
            writer.writerow([
                pedido.id,
                f"{pedido.cliente.nombre} {pedido.cliente.apellido}",
                pedido.fecha_pedido.strftime('%Y-%m-%d %H:%M'),
                pedido.get_estado_display(),
                pedido.get_total()
            ])
        
        self.message_user(request, f'{queryset.count()} pedidos exportados correctamente.')
        return response
    exportar_csv.short_description = '📥 Exportar a CSV'