from django.contrib import admin
from django.db.models import Sum, Count
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from django.urls import path, reverse
from .views import get_admin_stats

# Importaciones de Modelos
from inventario.models import Producto, Categoria
from pedidos.models import Pedido
from usuarios.models import Usuario
from cotizaciones.models import Cotizacion, DetalleCotizacion
from ventas.models import Factura, ItemFactura
from core.utils import formato_pesos


# ==================== COTIZACIONES ====================

class DetallesCotizacionEnLinea(admin.TabularInline):
    model = DetalleCotizacion
    extra = 1
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal_display', 'notas')
    readonly_fields = ('subtotal_display',)
    
    def subtotal_display(self, obj):
        """Muestra el subtotal calculado"""
        from decimal import Decimal
        if obj.precio_unitario and obj.cantidad:
            subtotal = obj.precio_unitario * obj.cantidad
            if obj.cotizacion.incluir_iva:
                subtotal = subtotal * Decimal('1.19')
            return f"${subtotal:,.2f}"
        return "---"
    subtotal_display.short_description = 'Subtotal'


class AdminCotizacion(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'fecha_solicitud', 'estado', 'total', 'num_items', 'acciones_lista']
    list_filter = ['estado', 'fecha_solicitud']
    search_fields = ['cliente__username', 'cliente__first_name', 'cliente__last_name']
    date_hierarchy = 'fecha_solicitud'
    readonly_fields = ['fecha_solicitud', 'enlace_descargar_pdf', 'total_display']
    inlines = [DetallesCotizacionEnLinea]

    fieldsets = (
        ('Información General', {
            'fields': ('cliente', 'fecha_solicitud', 'estado', 'vigencia', 'incluir_iva')
        }),
        ('Notas', {
            'fields': ('notas_cliente', 'notas_admin', 'fecha_respuesta')
        }),
        ('Acciones Disponibles', {
            'fields': ('enlace_descargar_pdf',),
            'classes': ('collapse',),
            'description': 'Acciones disponibles después de guardar la cotización'
        }),
    )

    def acciones_lista(self, obj):
        """Botones de acción en la lista del admin"""
        botones = ''
        
        if obj.estado == 'pendiente':
            url_responder = reverse('cotizaciones:responder_cotizacion', args=[obj.pk])
            botones += f'<a class="button" href="{url_responder}" style="background-color: #417690; padding: 5px 10px; border-radius: 3px; color: white; text-decoration: none; margin-right: 5px;">📧 Responder</a>'
        
        url_pdf = reverse('cotizaciones:descargar_pdf', args=[obj.pk])
        botones += f'<a class="button" href="{url_pdf}" style="background-color: #d9534f; padding: 5px 10px; border-radius: 3px; color: white; text-decoration: none;">📄 PDF</a>'
        
        return mark_safe(botones)
    acciones_lista.short_description = 'Acciones'

    def enlace_descargar_pdf(self, obj):
        """Botón para descargar PDF en el detalle"""
        if obj.pk is None:
            return mark_safe('<span class="text-muted">Disponible después de guardar</span>')
        
        url_pdf = reverse('cotizaciones:descargar_pdf', args=[obj.pk])
        return mark_safe(
            f'<a class="button" href="{url_pdf}" target="_blank" style="background-color: #d9534f; padding: 8px 15px; '
            f'border-radius: 4px; color: white; text-decoration: none; display: inline-block;">'
            f'📄 Descargar PDF</a>'
        )
    enlace_descargar_pdf.short_description = 'Descargar Cotización'

    def total_display(self, obj):
        """Muestra el total calculado con IVA"""
        total = obj.total
        return mark_safe(
            f'<span id="total-display" style="font-size: 18px; font-weight: bold; color: #28a745;">'
            f'${total:,.2f}</span>'
        )
    total_display.short_description = 'Total Final'


admin.site.register(Cotizacion, AdminCotizacion)


# ==================== FACTURACIÓN ====================

class ItemFacturaEnLinea(admin.TabularInline):
    model = ItemFactura
    extra = 1
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal_display', 'boton_recalcular')
    readonly_fields = ('subtotal_display', 'boton_recalcular')
    autocomplete_fields = ['producto']

    def boton_recalcular(self, obj):
        """Botón para recalcular el subtotal"""
        return mark_safe(
            '<button type="button" class="recalcular-btn" data-id="%s" '
            'style="background-color: #417690; padding: 5px 10px; border-radius: 3px; '
            'color: white; border: none; cursor: pointer;">🔄 Recalcular</button>' % (obj.pk if obj.pk else '')
        )
    boton_recalcular.short_description = 'Acción'

    def subtotal_display(self, obj):
        """Muestra el subtotal calculado"""
        from decimal import Decimal
        if obj.precio_unitario and obj.cantidad:
            subtotal = obj.precio_unitario * obj.cantidad
            return f"${subtotal:,.2f}"
        return "---"
    subtotal_display.short_description = 'Subtotal'

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form

        form.base_fields['producto'].widget.attrs.update({
            'onchange': 'actualizarPrecioUnitario(this);'
        })

        return formset


class AdminFactura(admin.ModelAdmin):
    inlines = [ItemFacturaEnLinea]
    list_display = ('numero', 'nombre_cliente', 'fecha_emision', 'mostrar_total', 'estado', 'con_iva', 'enlace_descargar_pdf')
    list_filter = ('estado', 'con_iva', 'fecha_emision')
    search_fields = ('numero', 'nombre_cliente', 'documento_cliente')
    readonly_fields = ('subtotal_display', 'valor_iva_display', 'total_display', 'fecha_creacion', 'fecha_actualizacion')
    fieldsets = (
        ('Información de Factura', {
            'fields': (('numero', 'fecha_emision'), 'estado')
        }),
        ('Cliente', {
            'fields': (('nombre_cliente', 'documento_cliente'),
                       ('direccion_cliente', 'telefono_cliente'),
                       'email_cliente', 'cliente')
        }),
        ('Totales', {
            'fields': (('subtotal_display', 'con_iva', 'porcentaje_iva'), ('valor_iva_display', 'total_display'))
        }),
        ('Notas y Registro', {
            'fields': ('notas', 'vendedor', ('fecha_creacion', 'fecha_actualizacion'))
        }),
    )

    def mostrar_total(self, obj):
        return format_html('<strong>${}</strong>', obj.total)
    mostrar_total.short_description = 'Total'

    def enlace_descargar_pdf(self, obj):
        """Muestra un enlace para descargar el PDF"""
        return format_html(
            '<a class="button" href="{}" style="background-color: #417690; padding: 5px 10px; border-radius: 3px; color: white; text-decoration: none;">📥 PDF</a>',
            reverse('admin:ventas_factura_descargar_pdf', args=[obj.pk])
        )
    enlace_descargar_pdf.short_description = 'Descargar'

    def subtotal_display(self, obj):
        """Muestra el subtotal calculado"""
        return mark_safe(
            f'<span id="subtotal-display" style="font-size: 16px; font-weight: bold;">'
            f'${obj.subtotal:,.2f}</span>'
        )
    subtotal_display.short_description = 'Subtotal'

    def valor_iva_display(self, obj):
        """Muestra el valor del IVA"""
        return mark_safe(
            f'<span id="valor-iva-display" style="font-size: 16px; font-weight: bold;">'
            f'${obj.valor_iva:,.2f}</span>'
        )
    valor_iva_display.short_description = 'Valor IVA'

    def total_display(self, obj):
        """Muestra el total calculado"""
        return mark_safe(
            f'<span id="total-display" style="font-size: 18px; font-weight: bold; color: #28a745;">'
            f'${obj.total:,.2f}</span>'
        )
    total_display.short_description = 'Total Final'

    def save_model(self, request, obj, form, change):
        if not change:
            if not obj.numero:
                obj.generar_numero()
            if not obj.vendedor:
                obj.vendedor = request.user

        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instancias = formset.save(commit=False)

        for instancia in instancias:
            if instancia.precio_unitario is None or instancia.precio_unitario == 0:
                instancia.precio_unitario = instancia.producto.precio

            instancia.subtotal = instancia.cantidad * instancia.precio_unitario
            instancia.save()

        for obj in formset.deleted_objects:
            obj.delete()

        formset.save_m2m()

        form.instance.calcular_totales()

    def descargar_pdf(self, request, object_id):
        """
        Vista personalizada para descargar la factura en PDF
        """
        from ventas.utils import generar_pdf_factura
        factura = self.get_object(request, object_id)
        
        pdf_buffer = generar_pdf_factura(factura)
        
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Factura_{factura.numero}.pdf"'
        
        return response
    
    def get_urls(self):
        """
        Agregar URLs personalizadas
        """
        urls = super().get_urls()
        custom_urls = [
            path(
                '<object_id>/descargar-pdf/',
                self.admin_site.admin_view(self.descargar_pdf),
                name='ventas_factura_descargar_pdf',
            ),
        ]
        return custom_urls + urls

    class Media:
        js = (
            'js/factura_admin.js',
        )


class AdminItemFactura(admin.ModelAdmin):
    list_display = ('factura', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('factura__estado',)
    search_fields = ('factura__numero', 'producto__nombre')
    autocomplete_fields = ['producto', 'factura']


