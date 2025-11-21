from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.http import HttpResponse
from datetime import datetime
import csv
from .models import Cotizacion, DetalleCotizacion

class DetalleCotizacionInline(admin.TabularInline):
    model = DetalleCotizacion
    extra = 1
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal_display', 'notas', 'recalcular_btn')
    readonly_fields = ('subtotal_display', 'recalcular_btn')
    autocomplete_fields = ['producto']
    
    def recalcular_btn(self, obj):
        """Botón para recalcular el subtotal"""
        return mark_safe(
            '<button type="button" class="recalcular-btn" data-id="%s" '
            'style="background-color: #417690; padding: 5px 10px; border-radius: 3px; '
            'color: white; border: none; cursor: pointer;">🔄 Recalcular</button>' % (obj.pk if obj.pk else '')
        )
    recalcular_btn.short_description = 'Acción'
    
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
    list_display = ['id_display', 'cliente_nombre', 'fecha_solicitud', 'estado_badge', 'total_display', 'num_items_display', 'acciones_list']
    list_filter = ['estado', 'fecha_solicitud', 'incluir_iva']
    search_fields = ['id', 'cliente__username', 'cliente__first_name', 'cliente__last_name', 'cliente__email']
    date_hierarchy = 'fecha_solicitud'
    readonly_fields = ['fecha_solicitud', 'descargar_pdf_link', 'total_display_detail', 'subtotal_display', 'iva_display']
    autocomplete_fields = ['cliente']
    list_per_page = 25

    fieldsets = (
        ('Información General', {
            'fields': ('cliente', 'fecha_solicitud', 'estado', 'vigencia', 'incluir_iva')
        }),
        ('Totales', {
            'fields': ('subtotal_display', 'iva_display', 'total_display_detail'),
            'classes': ('wide',)
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
    
    actions = ['cambiar_a_revisada', 'cambiar_a_aprobada', 'cambiar_a_rechazada', 'exportar_csv']

    def get_inline_instances(self, request, obj=None):
        """Muestra los inlines después de los fieldsets principales"""
        return [DetalleCotizacionInline(self.model, self.admin_site)]

    def change_view(self, request, object_id=None, form_url='', extra_context=None):
        """Agrega un botón de recalcular todos en el contexto"""
        extra_context = extra_context or {}
        extra_context['show_recalcular_all'] = True
        return super().change_view(request, object_id, form_url, extra_context)
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        qs = super().get_queryset(request)
        return qs.select_related('cliente').prefetch_related('items__producto')
    
    def id_display(self, obj):
        """Muestra el ID con formato"""
        return format_html('<strong>#{}</strong>', obj.id)
    id_display.short_description = 'ID'
    id_display.admin_order_field = 'id'
    
    def cliente_nombre(self, obj):
        """Muestra el nombre del cliente"""
        return obj.cliente.get_full_name() or obj.cliente.username
    cliente_nombre.short_description = 'Cliente'
    cliente_nombre.admin_order_field = 'cliente__first_name'
    
    def estado_badge(self, obj):
        """Muestra el estado con badge de colores"""
        colors = {
            'pendiente': '#ffc107',
            'revisada': '#17a2b8',
            'aprobada': '#28a745',
            'rechazada': '#dc3545',
            'convertida': '#6c757d',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 12px; border-radius: 15px; font-weight: bold;">{}</span>',
            colors.get(obj.estado, '#6c757d'),
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    estado_badge.admin_order_field = 'estado'
    
    def total_display(self, obj):
        """Muestra el total en la lista"""
        return format_html(
            '<span style="font-weight: bold; color: #28a745;">${:,.2f}</span>',
            obj.total
        )
    total_display.short_description = 'Total'
    
    def total_display_detail(self, obj):
        """Muestra el total en el detalle"""
        return mark_safe(
            f'<span id="total-display" style="font-size: 20px; font-weight: bold; color: #28a745;">'
            f'${obj.total:,.2f}</span>'
        )
    total_display_detail.short_description = 'Total Final'
    
    def subtotal_display(self, obj):
        """Muestra el subtotal sin IVA"""
        return mark_safe(
            f'<span style="font-size: 16px; font-weight: bold;">${obj.subtotal_sin_iva:,.2f}</span>'
        )
    subtotal_display.short_description = 'Subtotal (sin IVA)'
    
    def iva_display(self, obj):
        """Muestra el valor del IVA"""
        return mark_safe(
            f'<span style="font-size: 16px; font-weight: bold;">${obj.iva:,.2f}</span>'
        )
    iva_display.short_description = 'IVA (19%)'
    
    def num_items_display(self, obj):
        """Muestra el número de items"""
        count = obj.num_items
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 3px 8px; border-radius: 10px;">{} items</span>',
            count
        )
    num_items_display.short_description = 'Items'

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
    
    # Acciones en lote
    def cambiar_a_revisada(self, request, queryset):
        """Cambia el estado a 'revisada'"""
        updated = queryset.update(estado='revisada')
        self.message_user(request, f'{updated} cotización(es) marcadas como "Revisada".')
    cambiar_a_revisada.short_description = '👁️ Marcar como Revisada'
    
    def cambiar_a_aprobada(self, request, queryset):
        """Cambia el estado a 'aprobada'"""
        updated = queryset.update(estado='aprobada')
        self.message_user(request, f'{updated} cotización(es) marcadas como "Aprobada".')
    cambiar_a_aprobada.short_description = '✅ Marcar como Aprobada'
    
    def cambiar_a_rechazada(self, request, queryset):
        """Cambia el estado a 'rechazada'"""
        updated = queryset.update(estado='rechazada')
        self.message_user(request, f'{updated} cotización(es) marcadas como "Rechazada".')
    cambiar_a_rechazada.short_description = '❌ Marcar como Rechazada'
    
    def exportar_csv(self, request, queryset):
        """Exportar cotizaciones a CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="cotizaciones.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Cliente', 'Fecha', 'Estado', 'Items', 'Total'])
        
        for cot in queryset:
            writer.writerow([
                cot.id,
                cot.cliente.get_full_name() or cot.cliente.username,
                cot.fecha_solicitud.strftime('%Y-%m-%d %H:%M'),
                cot.get_estado_display(),
                cot.num_items,
                cot.total
            ])
        
        self.message_user(request, f'{queryset.count()} cotizaciones exportadas correctamente.')
        return response
    exportar_csv.short_description = '📥 Exportar a CSV'
