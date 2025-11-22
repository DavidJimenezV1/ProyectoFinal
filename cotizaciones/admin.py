from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Cotizacion, DetalleCotizacion


class DetalleCotizacionInline(admin.TabularInline):
    model = DetalleCotizacion
    extra = 1
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal_display', 'notas')
    readonly_fields = ('subtotal_display',)
    
    def subtotal_display(self, obj):
        """Muestra el subtotal calculado"""
        from decimal import Decimal
        if obj.precio_unitario and obj.cantidad:
            subtotal = obj.precio_unitario * obj.cantidad
            # Aplicar IVA si está habilitado en la cotización
            if obj.cotizacion.incluir_iva:
                subtotal = subtotal * Decimal('1.19')
            return f"${subtotal:,.2f}"
        return "---"
    subtotal_display.short_description = 'Subtotal'


@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display = ['id_colored', 'cliente_colored', 'fecha_colored', 'estado_colored', 'total_colored', 'num_items_colored', 'acciones_list']
    list_filter = ['estado', 'fecha_solicitud']
    search_fields = ['cliente__username', 'cliente__first_name', 'cliente__last_name']
    date_hierarchy = 'fecha_solicitud'
    readonly_fields = ['fecha_solicitud', 'descargar_pdf_link', 'total_display']
    inlines = [DetalleCotizacionInline]

    fieldsets = (
        ('Información General', {
            'fields': ('cliente', 'fecha_solicitud', 'estado', 'vigencia', 'incluir_iva')
        }),
        ('Notas', {
            'fields': ('notas_cliente', 'notas_admin', 'fecha_respuesta')
        }),
        ('Acciones Disponibles', {
            'fields': ('descargar_pdf_link',),
            'classes': ('collapse',),
            'description': 'Acciones disponibles después de guardar la cotización'
        }),
    )

    # ==================== MÉTODOS CON COLORES ====================
    
    def id_colored(self, obj):
        """ID con fondo AZUL y letras BLANCAS"""
        return mark_safe(
            f'<span style="background-color: #4169E1; color: white; padding: 8px 12px; '
            f'border-radius: 4px; font-weight: 900; display: inline-block;">{obj.id}</span>'
        )
    id_colored.short_description = 'ID'

    def cliente_colored(self, obj):
        """Cliente con fondo PÚRPURA y letras BLANCAS"""
        cliente_nombre = obj.cliente.get_full_name() or obj.cliente.username
        return mark_safe(
            f'<span style="background-color: #8B5FBF; color: white; padding: 8px 12px; '
            f'border-radius: 4px; font-weight: 900; display: inline-block;">{cliente_nombre}</span>'
        )
    cliente_colored.short_description = 'Cliente'

    def fecha_colored(self, obj):
        """Fecha con fondo VERDE y letras BLANCAS"""
        fecha = obj.fecha_solicitud.strftime('%d/%m/%Y %H:%M')
        return mark_safe(
            f'<span style="background-color: #27AE60; color: white; padding: 8px 12px; '
            f'border-radius: 4px; font-weight: 900; display: inline-block;">{fecha}</span>'
        )
    fecha_colored.short_description = 'Fecha de Solicitud'

    def estado_colored(self, obj):
        """Estado con color dinámico según estado"""
        colores = {
            'pendiente': '#FF9800',
            'revisada': '#2196F3',
            'aprobada': '#4CAF50',
            'rechazada': '#F44336',
            'convertida': '#9C27B0',
        }
        color = colores.get(obj.estado, '#757575')
        estado_display = dict(obj.ESTADO_CHOICES).get(obj.estado, obj.estado)
        return mark_safe(
            f'<span style="background-color: {color}; color: white; padding: 8px 12px; '
            f'border-radius: 4px; font-weight: 900; display: inline-block;">{estado_display}</span>'
        )
    estado_colored.short_description = 'Estado'

    def total_colored(self, obj):
        """Total con fondo ROJO y letras BLANCAS"""
        return mark_safe(
            f'<span style="background-color: #E74C3C; color: white; padding: 8px 12px; '
            f'border-radius: 4px; font-weight: 900; display: inline-block;">${obj.total:,.2f}</span>'
        )
    total_colored.short_description = 'Total'

    def num_items_colored(self, obj):
        """Número de items con fondo NARANJA y letras BLANCAS"""
        return mark_safe(
            f'<span style="background-color: #FF6B35; color: white; padding: 8px 12px; '
            f'border-radius: 4px; font-weight: 900; display: inline-block;">{obj.num_items}</span>'
        )
    num_items_colored.short_description = 'Items'

    def acciones_list(self, obj):
        """Botones de acción en la lista del admin"""
        buttons = ''
        
        # Botón Responder
        if obj.estado == 'pendiente':
            responder_url = reverse('cotizaciones:responder_cotizacion', args=[obj.pk])
            buttons += f'<a class="button" href="{responder_url}" style="background-color: #417690; padding: 5px 10px; border-radius: 3px; color: white; text-decoration: none; margin-right: 5px;">📧 Responder</a>'
        
        # Botón Descargar PDF
        pdf_url = reverse('cotizaciones:descargar_pdf', args=[obj.pk])
        buttons += f'<a class="button" href="{pdf_url}" style="background-color: #d9534f; padding: 5px 10px; border-radius: 3px; color: white; text-decoration: none;">📄 PDF</a>'
        
        return mark_safe(buttons)
    acciones_list.short_description = 'Acciones'

    def descargar_pdf_link(self, obj):
        """Botón para descargar PDF en el detalle"""
        if obj.pk is None:
            return mark_safe('<span class="text-muted">Disponible después de guardar</span>')
        
        pdf_url = reverse('cotizaciones:descargar_pdf', args=[obj.pk])
        return mark_safe(
            f'<a class="button" href="{pdf_url}" target="_blank" style="background-color: #d9534f; padding: 8px 15px; '
            f'border-radius: 4px; color: white; text-decoration: none; display: inline-block;">'
            f'📄 Descargar PDF</a>'
        )
    descargar_pdf_link.short_description = 'Descargar Cotización'

    def total_display(self, obj):
        """Muestra el total calculado con IVA"""
        total = obj.total
        return mark_safe(
            f'<span id="total-display" style="font-size: 18px; font-weight: bold; color: #28a745;">'
            f'${total:,.2f}</span>'
        )
    total_display.short_description = 'Total Final'