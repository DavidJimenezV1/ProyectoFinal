from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings
import json


class AuditLog(models.Model):
    """
    Modelo principal para auditoría general del sistema.
    Registra todas las acciones CREATE, UPDATE, DELETE en cualquier modelo.
    """
    ACTION_CREATE = 'CREATE'
    ACTION_UPDATE = 'UPDATE'
    ACTION_DELETE = 'DELETE'
    
    ACTION_CHOICES = [
        (ACTION_CREATE, 'Crear'),
        (ACTION_UPDATE, 'Actualizar'),
        (ACTION_DELETE, 'Eliminar'),
    ]
    
    # Información del usuario
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuario"
    )
    usuario_nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre de usuario",
        help_text="Se guarda por si el usuario se elimina"
    )
    
    # Información de la acción
    accion = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES,
        verbose_name="Acción"
    )
    fecha_hora = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y hora",
        db_index=True
    )
    
    # Objeto afectado (GenericForeignKey para cualquier modelo)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name="Tipo de contenido"
    )
    object_id = models.PositiveIntegerField(verbose_name="ID del objeto")
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Datos adicionales
    modelo = models.CharField(
        max_length=100,
        verbose_name="Modelo",
        db_index=True
    )
    objeto_repr = models.CharField(
        max_length=200,
        verbose_name="Representación del objeto"
    )
    
    # Cambios realizados (JSON)
    cambios = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Cambios realizados",
        help_text="Datos anteriores y nuevos en formato JSON"
    )
    
    # Información adicional
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP"
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name="User Agent"
    )
    notas = models.TextField(
        blank=True,
        verbose_name="Notas adicionales"
    )
    
    class Meta:
        verbose_name = "Registro de auditoría"
        verbose_name_plural = "Registros de auditoría"
        ordering = ['-fecha_hora']
        indexes = [
            models.Index(fields=['-fecha_hora']),
            models.Index(fields=['modelo', '-fecha_hora']),
            models.Index(fields=['usuario', '-fecha_hora']),
            models.Index(fields=['accion', '-fecha_hora']),
        ]
    
    def __str__(self):
        return f"{self.accion} - {self.modelo} - {self.usuario_nombre} - {self.fecha_hora}"
    
    @property
    def cambios_formateados(self):
        """Devuelve los cambios en formato legible"""
        if not self.cambios:
            return "Sin cambios registrados"
        
        try:
            return json.dumps(self.cambios, indent=2, ensure_ascii=False)
        except:
            return str(self.cambios)


class HistorialProducto(models.Model):
    """Historial específico para cambios en productos"""
    producto = models.ForeignKey(
        'inventario.Producto',
        on_delete=models.CASCADE,
        related_name='historial',
        verbose_name="Producto"
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuario"
    )
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora")
    
    # Campos del producto que cambiaron
    nombre_anterior = models.CharField(max_length=100, blank=True)
    nombre_nuevo = models.CharField(max_length=100, blank=True)
    
    precio_anterior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    precio_nuevo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    stock_anterior = models.IntegerField(null=True, blank=True)
    stock_nuevo = models.IntegerField(null=True, blank=True)
    
    descripcion = models.TextField(verbose_name="Descripción del cambio")
    
    class Meta:
        verbose_name = "Historial de producto"
        verbose_name_plural = "Historiales de productos"
        ordering = ['-fecha_hora']
    
    def __str__(self):
        return f"{self.producto} - {self.fecha_hora}"


class HistorialPedido(models.Model):
    """Historial específico para cambios en pedidos"""
    pedido = models.ForeignKey(
        'pedidos.Pedido',
        on_delete=models.CASCADE,
        related_name='historial',
        verbose_name="Pedido"
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuario"
    )
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora")
    
    estado_anterior = models.CharField(max_length=20, blank=True)
    estado_nuevo = models.CharField(max_length=20, blank=True)
    
    descripcion = models.TextField(verbose_name="Descripción del cambio")
    
    class Meta:
        verbose_name = "Historial de pedido"
        verbose_name_plural = "Historiales de pedidos"
        ordering = ['-fecha_hora']
    
    def __str__(self):
        return f"Pedido #{self.pedido.id} - {self.fecha_hora}"


class HistorialCotizacion(models.Model):
    """Historial específico para cambios en cotizaciones"""
    cotizacion = models.ForeignKey(
        'cotizaciones.Cotizacion',
        on_delete=models.CASCADE,
        related_name='historial',
        verbose_name="Cotización"
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuario"
    )
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora")
    
    estado_anterior = models.CharField(max_length=20, blank=True)
    estado_nuevo = models.CharField(max_length=20, blank=True)
    
    total_anterior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_nuevo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    descripcion = models.TextField(verbose_name="Descripción del cambio")
    
    class Meta:
        verbose_name = "Historial de cotización"
        verbose_name_plural = "Historiales de cotizaciones"
        ordering = ['-fecha_hora']
    
    def __str__(self):
        return f"Cotización #{self.cotizacion.id} - {self.fecha_hora}"


class HistorialFactura(models.Model):
    """Historial específico para cambios en facturas"""
    factura = models.ForeignKey(
        'ventas.Factura',
        on_delete=models.CASCADE,
        related_name='historial',
        verbose_name="Factura"
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuario"
    )
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora")
    
    estado_anterior = models.CharField(max_length=20, blank=True)
    estado_nuevo = models.CharField(max_length=20, blank=True)
    
    total_anterior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_nuevo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    descripcion = models.TextField(verbose_name="Descripción del cambio")
    
    class Meta:
        verbose_name = "Historial de factura"
        verbose_name_plural = "Historiales de facturas"
        ordering = ['-fecha_hora']
    
    def __str__(self):
        return f"Factura {self.factura.numero} - {self.fecha_hora}"


class HistorialCliente(models.Model):
    """Historial específico para cambios en clientes"""
    cliente = models.ForeignKey(
        'pedidos.Cliente',
        on_delete=models.CASCADE,
        related_name='historial',
        verbose_name="Cliente"
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuario"
    )
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora")
    
    cambios = models.JSONField(default=dict, blank=True, verbose_name="Cambios realizados")
    descripcion = models.TextField(verbose_name="Descripción del cambio")
    
    class Meta:
        verbose_name = "Historial de cliente"
        verbose_name_plural = "Historiales de clientes"
        ordering = ['-fecha_hora']
    
    def __str__(self):
        return f"{self.cliente} - {self.fecha_hora}"


class HistorialCategoria(models.Model):
    """Historial específico para cambios en categorías"""
    categoria = models.ForeignKey(
        'inventario.Categoria',
        on_delete=models.CASCADE,
        related_name='historial',
        verbose_name="Categoría"
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuario"
    )
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora")
    
    nombre_anterior = models.CharField(max_length=100, blank=True)
    nombre_nuevo = models.CharField(max_length=100, blank=True)
    
    descripcion = models.TextField(verbose_name="Descripción del cambio")
    
    class Meta:
        verbose_name = "Historial de categoría"
        verbose_name_plural = "Historiales de categorías"
        ordering = ['-fecha_hora']
    
    def __str__(self):
        return f"{self.categoria} - {self.fecha_hora}"
