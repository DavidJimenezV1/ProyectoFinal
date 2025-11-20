from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from django.urls import path, reverse
from .models import Factura, ItemFactura
from .utils import generar_pdf_factura

class ItemFacturaInline(admin.TabularInline):
    model = ItemFactura
    extra = 1
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal_display', 'recalcular_btn')
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
            return f"${subtotal:,.2f}"
        return "---"
    subtotal_display.short_description = 'Subtotal'

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form

        # Al seleccionar un producto, autocompletar el precio
        form.base_fields['producto'].widget.attrs.update({
            'onchange': 'updatePrecioUnitario(this);'
        })

        return formset

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    inlines = [ItemFacturaInline]
    list_display = ('numero', 'nombre_cliente', 'fecha_emision', 'mostrar_total', 'estado', 'con_iva', 'descargar_pdf_link')
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

    def descargar_pdf_link(self, obj):
        """Muestra un enlace para descargar el PDF"""
        return format_html(
            '<a class="button" href="{}" style="background-color: #417690; padding: 5px 10px; border-radius: 3px; color: white; text-decoration: none;">📥 PDF</a>',
            reverse('admin:ventas_factura_descargar_pdf', args=[obj.pk])
        )
    descargar_pdf_link.short_description = 'Descargar'

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
        if not change:  # Si es una nueva factura
            # Generar número automático si no se proporcionó
            if not obj.numero:
                obj.generar_numero()
            # Asignar el usuario actual como vendedor
            if not obj.vendedor:
                obj.vendedor = request.user

        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        # Para cada item en el formset
        for instance in instances:
            # Si el precio unitario está vacío, usar el precio del producto
            if instance.precio_unitario is None or instance.precio_unitario == 0:
                instance.precio_unitario = instance.producto.precio

            # Calcular el subtotal
            instance.subtotal = instance.cantidad * instance.precio_unitario
            instance.save()

        # Manejar eliminaciones
        for obj in formset.deleted_objects:
            obj.delete()

        formset.save_m2m()

        # Recalcular totales de la factura
        form.instance.calcular_totales()

    def descargar_pdf(self, request, object_id):
        """
        Vista personalizada para descargar la factura en PDF
        """
        factura = self.get_object(request, object_id)
        
        # Generar PDF
        pdf_buffer = generar_pdf_factura(factura)
        
        # Crear respuesta HTTP
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

@admin.register(ItemFactura)
class ItemFacturaAdmin(admin.ModelAdmin):
    list_display = ('factura', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('factura__estado',)
    search_fields = ('factura__numero', 'producto__nombre')
    autocomplete_fields = ['producto', 'factura']

# Cambiar el título del admin
admin.site.site_header = 'Tejos Olímpica - Administración'
admin.site.site_title = 'Tejos Olímpica'
admin.site.index_title = 'Panel de Control'
