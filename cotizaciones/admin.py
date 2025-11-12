from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Cotizacion, DetalleCotizacion

class DetalleCotizacionInline(admin.TabularInline):
    model = DetalleCotizacion
    extra = 1
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal_display', 'notas', 'recalcular_btn')
    readonly_fields = ('subtotal_display', 'recalcular_btn')
    
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
    list_display = ['id', 'cliente', 'fecha_solicitud', 'estado', 'total', 'num_items', 'acciones_list']
    list_filter = ['estado', 'fecha_solicitud']
    search_fields = ['cliente__username', 'cliente__first_name', 'cliente__last_name']
    date_hierarchy = 'fecha_solicitud'
    readonly_fields = ['fecha_solicitud', 'descargar_pdf_link', 'total_display']

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

    def get_inline_instances(self, request, obj=None):
        """Muestra los inlines después de los fieldsets principales"""
        return [DetalleCotizacionInline(self.model, self.admin_site)]

    def change_view(self, request, object_id=None, form_url='', extra_context=None):
        """Agrega un botón de recalcular todos en el contexto"""
        extra_context = extra_context or {}
        extra_context['show_recalcular_all'] = True
        return super().change_view(request, object_id, form_url, extra_context)

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
