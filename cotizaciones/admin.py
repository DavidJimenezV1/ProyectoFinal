from django.contrib import admin
from .models import Cotizacion, DetalleCotizacion

class DetalleCotizacionInline(admin.TabularInline):
    model = DetalleCotizacion
    extra = 1

@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'fecha_solicitud', 'estado', 'total', 'num_items']
    list_filter = ['estado', 'fecha_solicitud']
    search_fields = ['cliente__username', 'cliente__first_name', 'cliente__last_name']
    date_hierarchy = 'fecha_solicitud'
    inlines = [DetalleCotizacionInline]
    readonly_fields = ['fecha_solicitud']
    
    fieldsets = (
        ('Información General', {
            'fields': ('cliente', 'fecha_solicitud', 'estado', 'vigencia')
        }),
        ('Notas', {
            'fields': ('notas_cliente', 'notas_admin', 'fecha_respuesta')
        }),
    )