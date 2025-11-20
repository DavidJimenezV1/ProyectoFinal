from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Producto, ImagenProducto

class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1
    fields = ['imagen', 'es_principal', 'orden', 'titulo']

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre_con_emoji', 'codigo', 'precio_con_formato', 'stock_con_alerta', 'categoria')
    search_fields = ('nombre', 'codigo', 'descripcion')
    list_filter = ('categoria',)
    inlines = [ImagenProductoInline]
    fieldsets = (
        ('Información básica', {
            'fields': ('nombre', 'codigo', 'categoria', 'descripcion')
        }),
        ('Inventario', {
            'fields': ('precio', 'stock', 'stock_minimo')
        }),
    )
    
    def nombre_con_emoji(self, obj):
        """Muestra el nombre del producto con un emoji"""
        return format_html('📦 <strong>{}</strong>', obj.nombre)
    nombre_con_emoji.short_description = 'Nombre'
    nombre_con_emoji.admin_order_field = 'nombre'
    
    def precio_con_formato(self, obj):
        """Muestra el precio con formato"""
        precio_formateado = f'${obj.precio:,.0f}'
        return format_html('<span style="color: #00B4A6; font-weight: bold;">{}</span>', precio_formateado)
    precio_con_formato.short_description = 'Precio'
    precio_con_formato.admin_order_field = 'precio'
    
    def stock_con_alerta(self, obj):
        """Muestra el stock con alerta si está bajo"""
        if obj.stock <= 0:
            color = '#E63946'
            emoji = '❌'
        elif obj.stock <= obj.stock_minimo:
            color = '#FFD60A'
            emoji = '⚠️'
        else:
            color = '#00B4A6'
            emoji = '✅'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, emoji, obj.stock
        )
    stock_con_alerta.short_description = 'Stock'
    stock_con_alerta.admin_order_field = 'stock'
    
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

@admin.register(ImagenProducto)
class ImagenProductoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'es_principal', 'orden', 'titulo')
    list_filter = ('es_principal', 'producto__categoria')
    search_fields = ('producto__nombre', 'titulo')
    list_editable = ('es_principal', 'orden', 'titulo')

admin.site.register(Producto, ProductoAdmin)
admin.site.register(Categoria)