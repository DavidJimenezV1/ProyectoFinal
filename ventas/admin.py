from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from django.urls import path, reverse
from datetime import datetime
import csv
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
    list_display = ('numero_display', 'nombre_cliente', 'fecha_emision', 'mostrar_total', 'estado_badge', 'con_iva_display', 'descargar_pdf_link')
    list_filter = ('estado', 'con_iva', 'fecha_emision')
    search_fields = ('numero', 'nombre_cliente', 'documento_cliente', 'email_cliente')
    date_hierarchy = 'fecha_emision'
    readonly_fields = ('subtotal_display', 'valor_iva_display', 'total_display', 'fecha_creacion', 'fecha_actualizacion')
    autocomplete_fields = ['cliente', 'vendedor']
    list_per_page = 25
    
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
    
    actions = ['cambiar_a_pagada', 'cambiar_a_cancelada', 'exportar_csv']

    def get_queryset(self, request):
        """Optimizar consultas"""
        qs = super().get_queryset(request)
        return qs.select_related('cliente', 'vendedor').prefetch_related('items__producto')

    def numero_display(self, obj):
        """Muestra el número con formato destacado"""
        return format_html('<strong style="font-size: 14px;">{}</strong>', obj.numero)
    numero_display.short_description = 'Número'
    numero_display.admin_order_field = 'numero'
    
    def estado_badge(self, obj):
        """Muestra el estado con badge de colores"""
        colors = {
            'pendiente': '#ffc107',
            'pagada': '#28a745',
            'cancelada': '#dc3545',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 12px; border-radius: 15px; font-weight: bold;">{}</span>',
            colors.get(obj.estado, '#6c757d'),
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    estado_badge.admin_order_field = 'estado'
    
    def con_iva_display(self, obj):
        """Muestra si incluye IVA"""
        if obj.con_iva:
            return format_html('✅ Sí')
        return format_html('❌ No')
    con_iva_display.short_description = 'Con IVA'

    def mostrar_total(self, obj):
        return format_html('<strong style="color: #28a745; font-size: 14px;">${:,.2f}</strong>', obj.total)
    mostrar_total.short_description = 'Total'
    mostrar_total.admin_order_field = 'total'

    def descargar_pdf_link(self, obj):
        """Muestra un enlace para descargar el PDF"""
        if obj.pk:
            return format_html(
                '<a class="button" href="{}" style="background-color: #417690; padding: 5px 10px; border-radius: 3px; color: white; text-decoration: none;">📥 PDF</a>',
                reverse('admin:ventas_factura_descargar_pdf', args=[obj.pk])
            )
        return '-'
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
    
    # Acciones en lote
    def cambiar_a_pagada(self, request, queryset):
        """Marca facturas como pagadas"""
        updated = queryset.update(estado='pagada')
        self.message_user(request, f'{updated} factura(s) marcadas como "Pagada".')
    cambiar_a_pagada.short_description = '✅ Marcar como Pagada'
    
    def cambiar_a_cancelada(self, request, queryset):
        """Marca facturas como canceladas"""
        updated = queryset.update(estado='cancelada')
        self.message_user(request, f'{updated} factura(s) marcadas como "Cancelada".')
    cambiar_a_cancelada.short_description = '❌ Marcar como Cancelada'
    
    def exportar_csv(self, request, queryset):
        """Exportar facturas a CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="facturas.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Número', 'Cliente', 'Fecha', 'Estado', 'Subtotal', 'IVA', 'Total'])
        
        for factura in queryset:
            writer.writerow([
                factura.numero,
                factura.nombre_cliente,
                factura.fecha_emision.strftime('%Y-%m-%d %H:%M'),
                factura.get_estado_display(),
                factura.subtotal,
                factura.valor_iva,
                factura.total
            ])
        
        self.message_user(request, f'{queryset.count()} facturas exportadas correctamente.')
        return response
    exportar_csv.short_description = '📥 Exportar a CSV'

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
