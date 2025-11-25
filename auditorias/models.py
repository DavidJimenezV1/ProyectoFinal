from django.db import models
<<<<<<< HEAD
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
import json


class AuditLog(models.Model):
    """Registro general de auditoría"""
    ACCIONES = [
        ('CREATE', '✅ CREADO'),
        ('UPDATE', '🔄 ACTUALIZADO'),
        ('DELETE', '❌ ELIMINADO'),
        ('VIEW', '👁️ VISUALIZADO'),
    ]
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    accion = models.CharField(max_length=20, choices=ACCIONES)
    modelo = models.CharField(max_length=100)
    objeto_id = models.IntegerField()
    objeto_nombre = models.CharField(max_length=255)
    
    # NUEVOS CAMPOS PARA ANTES/DESPUÉS
    datos_anterior = models.JSONField(null=True, blank=True, help_text="Datos antes de la modificación")
    datos_nuevo = models.JSONField(null=True, blank=True, help_text="Datos después de la modificación")
    cambios = models.JSONField(null=True, blank=True, help_text="Solo los campos que cambiaron")
    
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Registro de Auditoría"
        verbose_name_plural = "Registros de Auditoría"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['usuario', '-timestamp']),
            models.Index(fields=['modelo', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_accion_display()} - {self.modelo} #{self.objeto_id} por {self.usuario}"
    
    @property
    def resumen(self):
        """Resumen legible del cambio"""
        if self.accion == 'CREATE':
            return f"✅ Se creó {self.modelo}: {self.objeto_nombre}"
        elif self.accion == 'DELETE':
            return f"❌ Se eliminó {self.modelo}: {self.objeto_nombre}"
        elif self.accion == 'UPDATE':
            cambios_texto = self._obtener_cambios_texto()
            return f"🔄 Se actualizó {self.modelo}: {self.objeto_nombre}\n{cambios_texto}"
        else:
            return f"👁️ Se visualizó {self.modelo}: {self.objeto_nombre}"
    
    def _obtener_cambios_texto(self):
        """Genera texto legible de los cambios"""
        if not self.cambios:
            return "Sin detalles de cambios"
        
        lineas = []
        for campo, (antes, despues) in self.cambios.items():
            lineas.append(f"  • {campo}: {antes} → {despues}")
        
        return "\n".join(lineas)


class HistorialProducto(models.Model):
    """Historial específico de cambios en Productos"""
    audit_log = models.OneToOneField(AuditLog, on_delete=models.CASCADE, related_name='historial_producto')
    producto_id = models.IntegerField()
    precio_anterior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    precio_nuevo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock_anterior = models.IntegerField(null=True, blank=True)
    stock_nuevo = models.IntegerField(null=True, blank=True)
    estado_anterior = models.CharField(max_length=50, null=True, blank=True)
    estado_nuevo = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        verbose_name = "Historial de Producto"
        verbose_name_plural = "Historiales de Producto"
        ordering = ['-audit_log__timestamp']
    
    def __str__(self):
        return f"Producto #{self.producto_id} - {self.audit_log.accion}"


class HistorialPedido(models.Model):
    """Historial específico de cambios en Pedidos"""
    audit_log = models.OneToOneField(AuditLog, on_delete=models.CASCADE, related_name='historial_pedido')
    pedido_id = models.IntegerField()
    estado_anterior = models.CharField(max_length=50, null=True, blank=True)
    estado_nuevo = models.CharField(max_length=50, null=True, blank=True)
    cliente_anterior = models.CharField(max_length=255, null=True, blank=True)
    cliente_nuevo = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        verbose_name = "Historial de Pedido"
        verbose_name_plural = "Historiales de Pedido"
        ordering = ['-audit_log__timestamp']
    
    def __str__(self):
        return f"Pedido #{self.pedido_id} - {self.audit_log.accion}"


class HistorialCotizacion(models.Model):
    """Historial específico de cambios en Cotizaciones"""
    audit_log = models.OneToOneField(AuditLog, on_delete=models.CASCADE, related_name='historial_cotizacion')
    cotizacion_id = models.IntegerField()
    estado_anterior = models.CharField(max_length=50, null=True, blank=True)
    estado_nuevo = models.CharField(max_length=50, null=True, blank=True)
    monto_anterior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monto_nuevo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        verbose_name = "Historial de Cotización"
        verbose_name_plural = "Historiales de Cotización"
        ordering = ['-audit_log__timestamp']
    
    def __str__(self):
        return f"Cotización #{self.cotizacion_id} - {self.audit_log.accion}"


class HistorialFactura(models.Model):
    """Historial específico de cambios en Facturas"""
    audit_log = models.OneToOneField(AuditLog, on_delete=models.CASCADE, related_name='historial_factura')
    factura_id = models.IntegerField()
    estado_anterior = models.CharField(max_length=50, null=True, blank=True)
    estado_nuevo = models.CharField(max_length=50, null=True, blank=True)
    monto_anterior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monto_nuevo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        verbose_name = "Historial de Factura"
        verbose_name_plural = "Historiales de Factura"
        ordering = ['-audit_log__timestamp']
    
    def __str__(self):
        return f"Factura #{self.factura_id} - {self.audit_log.accion}"


class HistorialCliente(models.Model):
    """Historial específico de cambios en Clientes"""
    audit_log = models.OneToOneField(AuditLog, on_delete=models.CASCADE, related_name='historial_cliente')
    cliente_id = models.IntegerField()
    cambios = models.JSONField(help_text="Cambios realizados")
    
    class Meta:
        verbose_name = "Historial de Cliente"
        verbose_name_plural = "Historiales de Cliente"
        ordering = ['-audit_log__timestamp']
    
    def __str__(self):
        return f"Cliente #{self.cliente_id} - {self.audit_log.accion}"


class HistorialCategoria(models.Model):
    """Historial específico de cambios en Categorías"""
    audit_log = models.OneToOneField(AuditLog, on_delete=models.CASCADE, related_name='historial_categoria')
    categoria_id = models.IntegerField()
    nombre_anterior = models.CharField(max_length=100, null=True, blank=True)
    nombre_nuevo = models.CharField(max_length=100, null=True, blank=True)
    descripcion_anterior = models.TextField(null=True, blank=True)
    descripcion_nueva = models.TextField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Historial de Categoría"
        verbose_name_plural = "Historiales de Categoría"
        ordering = ['-audit_log__timestamp']
    
    def __str__(self):
        return f"Categoría #{self.categoria_id} - {self.audit_log.accion}"
=======

class AuditLog(models.Model):
    action = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField()
    changes = models.JSONField()

    def __str__(self):
        return f"{self.action} on {self.model_name} (ID: {self.object_id}) at {self.timestamp}"

class UserAction(models.Model):
    audit_log = models.ForeignKey(AuditLog, related_name='user_actions', on_delete=models.CASCADE)
    description = models.TextField()

    def __str__(self):
        return self.description
>>>>>>> 2ccf0aabe78d0f7aa0a68ef0a71d1f968443289f
