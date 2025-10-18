from django.contrib import admin
from django.utils.html import format_html
from .models import Factura, ItemFactura

class ItemFacturaInline(admin.TabularInline):
    model = ItemFactura
    extra = 1
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')
    readonly_fields = ('subtotal',)
    autocomplete_fields = ['producto']
    
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
    list_display = ('numero', 'nombre_cliente', 'fecha_emision', 'mostrar_total', 'estado', 'con_iva')
    list_filter = ('estado', 'con_iva', 'fecha_emision')
    search_fields = ('numero', 'nombre_cliente', 'documento_cliente')
    readonly_fields = ('subtotal', 'valor_iva', 'total', 'fecha_creacion', 'fecha_actualizacion')
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
            'fields': (('subtotal', 'con_iva', 'porcentaje_iva'), ('valor_iva', 'total'))
        }),
        ('Notas y Registro', {
            'fields': ('notas', 'vendedor', ('fecha_creacion', 'fecha_actualizacion'))
        }),
    )
    
    def mostrar_total(self, obj):
        return format_html('<strong>${}</strong>', obj.total)
    mostrar_total.short_description = 'Total'
    
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