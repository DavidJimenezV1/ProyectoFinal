from django.contrib import admin
from django.utils.html import format_html
from .models import Cliente, Pedido, DetallePedido

class DetalleInline(admin.TabularInline):
    model = DetallePedido
    extra = 1

class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo_con_emoji', 'email', 'telefono')
    search_fields = ('nombre', 'apellido', 'email')
    
    def nombre_completo_con_emoji(self, obj):
        """Muestra el nombre completo con emoji"""
        return format_html('👤 <strong>{} {}</strong>', obj.nombre, obj.apellido)
    nombre_completo_con_emoji.short_description = 'Cliente'
    
    class Media:
        css = {
            'all': (
                'admin/css/admin_custom.css',
                'admin/css/animations.css',
            )
        }
        js = (
            'admin/js/admin_custom.js',
        )

class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id_con_emoji', 'cliente', 'fecha_pedido', 'fecha_entrega', 'estado_con_emoji')
    list_filter = ('estado', 'fecha_pedido')
    search_fields = ('cliente__nombre', 'cliente__apellido')
    inlines = [DetalleInline]
    
    def id_con_emoji(self, obj):
        """Muestra el ID con emoji"""
        return format_html('🛒 <strong>#{}</strong>', obj.id)
    id_con_emoji.short_description = 'Pedido'
    id_con_emoji.admin_order_field = 'id'
    
    def estado_con_emoji(self, obj):
        """Muestra el estado con emoji y color"""
        # Asumiendo que el modelo Pedido tiene un campo estado con choices
        emojis = {
            'pendiente': '⏳',
            'en_proceso': '🔄',
            'completado': '✅',
            'cancelado': '❌',
            'entregado': '📦'
        }
        colores = {
            'pendiente': '#FFD60A',
            'en_proceso': '#004E89',
            'completado': '#00B4A6',
            'cancelado': '#E63946',
            'entregado': '#8338EC'
        }
        estado_actual = obj.estado if hasattr(obj, 'estado') else 'pendiente'
        emoji = emojis.get(estado_actual, '❓')
        color = colores.get(estado_actual, '#666')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, emoji, estado_actual.replace('_', ' ').title()
        )
    estado_con_emoji.short_description = 'Estado'
    
    class Media:
        css = {
            'all': (
                'admin/css/admin_custom.css',
                'admin/css/animations.css',
            )
        }
        js = (
            'admin/js/admin_custom.js',
        )

admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Pedido, PedidoAdmin)