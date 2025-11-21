from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
from django.db.models import Q, F
import csv
from .models import Categoria, Producto, ImagenProducto
from django.db import models

class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1
    fields = ['imagen', 'es_principal', 'orden', 'titulo']

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'precio', 'stock_display', 'categoria', 'estado_stock')
    search_fields = ('nombre', 'codigo', 'descripcion')
    list_filter = ('categoria', 'fecha_creacion')
    inlines = [ImagenProductoInline]
    autocomplete_fields = ['categoria']
    list_per_page = 25
    
    fieldsets = (
        ('Información básica', {
            'fields': ('nombre', 'codigo', 'categoria', 'descripcion')
        }),
        ('Inventario', {
            'fields': ('precio', 'stock', 'stock_minimo')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    actions = ['exportar_csv', 'marcar_bajo_stock', 'aumentar_stock']
    
    def get_queryset(self, request):
        """Optimizar consultas con select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('categoria')
    
    def stock_display(self, obj):
        """Muestra el stock con formato"""
        return f"{obj.stock} unidades"
    stock_display.short_description = 'Stock'
    stock_display.admin_order_field = 'stock'
    
    def estado_stock(self, obj):
        """Indica el estado del stock con colores"""
        if obj.stock <= 0:
            color = 'red'
            estado = '❌ Agotado'
        elif obj.stock <= obj.stock_minimo:
            color = 'orange'
            estado = '⚠️ Bajo'
        else:
            color = 'green'
            estado = '✅ Normal'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, estado
        )
    estado_stock.short_description = 'Estado Stock'
    
    def exportar_csv(self, request, queryset):
        """Exportar productos a CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="productos.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Código', 'Nombre', 'Categoría', 'Precio', 'Stock', 'Stock Mínimo'])
        
        for producto in queryset:
            writer.writerow([
                producto.codigo,
                producto.nombre,
                producto.categoria.nombre,
                producto.precio,
                producto.stock,
                producto.stock_minimo
            ])
        
        self.message_user(request, f'{queryset.count()} productos exportados correctamente.')
        return response
    exportar_csv.short_description = '📥 Exportar a CSV'
    
    def marcar_bajo_stock(self, request, queryset):
        """Acción personalizada para marcar productos con bajo stock"""
        bajo_stock = queryset.filter(stock__lte=F('stock_minimo'))
        count = bajo_stock.count()
        self.message_user(request, f'{count} productos tienen stock bajo o agotado.')
    marcar_bajo_stock.short_description = '⚠️ Identificar bajo stock'
    
    def aumentar_stock(self, request, queryset):
        """Acción para aumentar stock en lote (ejemplo)"""
        # Esta es una acción de ejemplo, en producción requeriría un formulario
        self.message_user(request, 'Use el formulario de edición individual para ajustar stock.')
    aumentar_stock.short_description = '📦 Ajustar stock'

@admin.register(ImagenProducto)
class ImagenProductoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'es_principal', 'orden', 'titulo', 'imagen_preview')
    list_filter = ('es_principal', 'producto__categoria')
    search_fields = ('producto__nombre', 'titulo')
    list_editable = ('es_principal', 'orden', 'titulo')
    autocomplete_fields = ['producto']
    
    def imagen_preview(self, obj):
        """Muestra una vista previa de la imagen"""
        if obj.imagen:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />',
                obj.imagen.url
            )
        return '-'
    imagen_preview.short_description = 'Vista previa'

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'cantidad_productos')
    search_fields = ('nombre', 'descripcion')
    list_per_page = 20
    
    def cantidad_productos(self, obj):
        """Muestra la cantidad de productos en la categoría"""
        count = obj.producto_set.count()
        return format_html(
            '<span style="background-color: #417690; color: white; padding: 3px 8px; border-radius: 10px;">{} productos</span>',
            count
        )
    cantidad_productos.short_description = 'Productos'

# Registrar los modelos
admin.site.register(Producto, ProductoAdmin)