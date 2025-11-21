from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta


class AuditoriaFechaFilter(admin.SimpleListFilter):
    """Filtro personalizado para fechas de auditoría"""
    
    title = _('Período de tiempo')
    parameter_name = 'fecha'
    
    def lookups(self, request, model_admin):
        return (
            ('hoy', _('Hoy')),
            ('ayer', _('Ayer')),
            ('ultima_semana', _('Última semana')),
            ('ultimo_mes', _('Último mes')),
            ('ultimo_trimestre', _('Último trimestre')),
        )
    
    def queryset(self, request, queryset):
        hoy = datetime.now()
        
        if self.value() == 'hoy':
            fecha_inicio = hoy.replace(hour=0, minute=0, second=0, microsecond=0)
            return queryset.filter(fecha_hora__gte=fecha_inicio)
        
        if self.value() == 'ayer':
            ayer = hoy - timedelta(days=1)
            fecha_inicio = ayer.replace(hour=0, minute=0, second=0, microsecond=0)
            fecha_fin = hoy.replace(hour=0, minute=0, second=0, microsecond=0)
            return queryset.filter(fecha_hora__gte=fecha_inicio, fecha_hora__lt=fecha_fin)
        
        if self.value() == 'ultima_semana':
            fecha_inicio = hoy - timedelta(days=7)
            return queryset.filter(fecha_hora__gte=fecha_inicio)
        
        if self.value() == 'ultimo_mes':
            fecha_inicio = hoy - timedelta(days=30)
            return queryset.filter(fecha_hora__gte=fecha_inicio)
        
        if self.value() == 'ultimo_trimestre':
            fecha_inicio = hoy - timedelta(days=90)
            return queryset.filter(fecha_hora__gte=fecha_inicio)


class AuditoriaAccionFilter(admin.SimpleListFilter):
    """Filtro personalizado para acciones de auditoría"""
    
    title = _('Tipo de acción')
    parameter_name = 'tipo_accion'
    
    def lookups(self, request, model_admin):
        return (
            ('CREATE', _('Creaciones')),
            ('UPDATE', _('Actualizaciones')),
            ('DELETE', _('Eliminaciones')),
        )
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(accion=self.value())


class AuditoriaModeloFilter(admin.SimpleListFilter):
    """Filtro personalizado para tipos de modelo"""
    
    title = _('Tipo de objeto')
    parameter_name = 'tipo_objeto'
    
    def lookups(self, request, model_admin):
        return (
            ('producto', _('Productos')),
            ('categoria', _('Categorías')),
            ('pedido', _('Pedidos')),
            ('cliente', _('Clientes')),
            ('cotizacion', _('Cotizaciones')),
            ('factura', _('Facturas')),
        )
    
    def queryset(self, request, queryset):
        from django.contrib.contenttypes.models import ContentType
        
        if self.value() == 'producto':
            ct = ContentType.objects.filter(app_label='inventario', model='producto').first()
            if ct:
                return queryset.filter(content_type=ct)
        
        if self.value() == 'categoria':
            ct = ContentType.objects.filter(app_label='inventario', model='categoria').first()
            if ct:
                return queryset.filter(content_type=ct)
        
        if self.value() == 'pedido':
            ct = ContentType.objects.filter(app_label='pedidos', model='pedido').first()
            if ct:
                return queryset.filter(content_type=ct)
        
        if self.value() == 'cliente':
            ct = ContentType.objects.filter(app_label='pedidos', model='cliente').first()
            if ct:
                return queryset.filter(content_type=ct)
        
        if self.value() == 'cotizacion':
            ct = ContentType.objects.filter(app_label='cotizaciones', model='cotizacion').first()
            if ct:
                return queryset.filter(content_type=ct)
        
        if self.value() == 'factura':
            ct = ContentType.objects.filter(app_label='ventas', model='factura').first()
            if ct:
                return queryset.filter(content_type=ct)
