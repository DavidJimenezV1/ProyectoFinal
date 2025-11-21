from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import json

class AuditLog(models.Model):
    """Registro central de todas las acciones en el sistema"""
    
    ACTION_CHOICES = [
        ('CREATE', 'Crear'),
        ('UPDATE', 'Actualizar'),
        ('DELETE', 'Eliminar'),
        ('VIEW', 'Ver'),
    ]
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='audit_logs')
    accion = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    modelo = models.CharField(max_length=100, db_index=True)
    objeto_id = models.PositiveIntegerField()
    objeto_nombre = models.CharField(max_length=255, blank=True)
    datos_anteriores = models.JSONField(null=True, blank=True)
    datos_nuevos = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    descripcion = models.TextField()
    cambios_resumidos = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['usuario', '-timestamp']),
            models.Index(fields=['modelo', '-timestamp']),
            models.Index(fields=['accion', '-timestamp']),
        ]
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
    
    def __str__(self):
        return f"{self.get_accion_display()} - {self.modelo} ({self.objeto_id}) - {self.usuario.username}"
    
    @staticmethod
    def get_logs_por_rango_fecha(usuario=None, modelo=None, dias=7):
        """Obtener logs de los últimos N días"""
        fecha_inicio = timezone.now() - timedelta(days=dias)
        logs = AuditLog.objects.filter(timestamp__gte=fecha_inicio)
        
        if usuario:
            logs = logs.filter(usuario=usuario)
        if modelo:
            logs = logs.filter(modelo=modelo)
        
        return logs
    
    @staticmethod
    def get_logs_hoy(usuario=None):
        """Logs de hoy"""
        today = timezone.now().date()
        logs = AuditLog.objects.filter(timestamp__date=today)
        if usuario:
            logs = logs.filter(usuario=usuario)
        return logs
    
    @staticmethod
    def get_logs_esta_semana(usuario=None):
        """Logs de esta semana"""
        return AuditLog.get_logs_por_rango_fecha(usuario, dias=7)
    
    @staticmethod
    def get_logs_este_mes(usuario=None):
        """Logs de este mes"""
        return AuditLog.get_logs_por_rango_fecha(usuario, dias=30)


class HistorialProducto(models.Model):
    """Historial específico de cambios en productos"""
    audit_log = models.OneToOneField(AuditLog, on_delete=models.CASCADE)
    producto_id = models.PositiveIntegerField()
    precio_anterior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    precio_nuevo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock_anterior = models.IntegerField(null=True, blank=True)
    stock_nuevo = models.IntegerField(null=True, blank=True)
    estado_anterior = models.CharField(max_length=50, null=True, blank=True)
    estado_nuevo = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Historial de Producto'
        verbose_name_plural = 'Historiales de Producto'
    
    def __str__(self):
        return f"Producto {self.producto_id} - {self.audit_log.accion}"


class HistorialPedido(models.Model):
    """Historial específico de cambios en pedidos"""
    audit_log = models.OneToOneField(AuditLog, on_delete=models.CASCADE)
    pedido_id = models.PositiveIntegerField()
    estado_anterior = models.CharField(max_length=50, null=True, blank=True)
    estado_nuevo = models.CharField(max_length=50, null=True, blank=True)
    total_anterior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_nuevo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cliente_anterior = models.CharField(max_length=255, null=True, blank=True)
    cliente_nuevo = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Historial de Pedido'
        verbose_name_plural = 'Historiales de Pedido'
    
    def __str__(self):
        return f"Pedido {self.pedido_id} - {self.audit_log.accion}"


class HistorialCotizacion(models.Model):
    """Historial específico de cambios en cotizaciones"""
    audit_log = models.OneToOneField(AuditLog, on_delete=models.CASCADE)
    cotizacion_id = models.PositiveIntegerField()
    estado_anterior = models.CharField(max_length=50, null=True, blank=True)
    estado_nuevo = models.CharField(max_length=50, null=True, blank=True)
    monto_anterior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monto_nuevo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Historial de Cotización'
        verbose_name_plural = 'Historiales de Cotización'
    
    def __str__(self):
        return f"Cotización {self.cotizacion_id} - {self.audit_log.accion}"


class HistorialFactura(models.Model):
    """Historial específico de cambios en facturas"""
    audit_log = models.OneToOneField(AuditLog, on_delete=models.CASCADE)
    factura_id = models.PositiveIntegerField()
    monto_anterior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monto_nuevo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estado_anterior = models.CharField(max_length=50, null=True, blank=True)
    estado_nuevo = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Historial de Factura'
        verbose_name_plural = 'Historiales de Factura'
    
    def __str__(self):
        return f"Factura {self.factura_id} - {self.audit_log.accion}"


class HistorialCliente(models.Model):
    """Historial específico de cambios en clientes"""
    audit_log = models.OneToOneField(AuditLog, on_delete=models.CASCADE)
    cliente_id = models.PositiveIntegerField()
    cambios = models.JSONField()
    
    class Meta:
        verbose_name = 'Historial de Cliente'
        verbose_name_plural = 'Historiales de Cliente'
    
    def __str__(self):
        return f"Cliente {self.cliente_id} - {self.audit_log.accion}"


class HistorialCategoria(models.Model):
    """Historial específico de cambios en categorías"""
    audit_log = models.OneToOneField(AuditLog, on_delete=models.CASCADE)
    categoria_id = models.PositiveIntegerField()
    nombre_anterior = models.CharField(max_length=255, null=True, blank=True)
    nombre_nuevo = models.CharField(max_length=255, null=True, blank=True)
    descripcion_anterior = models.TextField(null=True, blank=True)
    descripcion_nueva = models.TextField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Historial de Categoría'
        verbose_name_plural = 'Historiales de Categoría'
    
    def __str__(self):
        return f"Categoría {self.categoria_id} - {self.audit_log.accion}"