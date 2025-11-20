from django.contrib import admin
from .models import Cliente, Pedido, DetallePedido

class DetalleInline(admin.TabularInline):
    model = DetallePedido
    extra = 1

class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'email', 'telefono')
    search_fields = ('nombre', 'apellido', 'email')

class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha_pedido', 'fecha_entrega', 'estado')
    list_filter = ('estado', 'fecha_pedido')
    search_fields = ('cliente__nombre', 'cliente__apellido')
    inlines = [DetalleInline]

admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Pedido, PedidoAdmin)