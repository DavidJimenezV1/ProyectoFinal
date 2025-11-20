from django.contrib import admin
from .models import Categoria, Producto, ImagenProducto

class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1
    fields = ['imagen', 'es_principal', 'orden', 'titulo']

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'precio', 'stock', 'categoria')
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

@admin.register(ImagenProducto)
class ImagenProductoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'es_principal', 'orden', 'titulo')
    list_filter = ('es_principal', 'producto__categoria')
    search_fields = ('producto__nombre', 'titulo')
    list_editable = ('es_principal', 'orden', 'titulo')

admin.site.register(Producto, ProductoAdmin)
admin.site.register(Categoria)