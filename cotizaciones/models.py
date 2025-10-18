from django.db import models
from django.conf import settings
from inventario.models import Producto

class Cotizacion(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de revisión'),
        ('revisada', 'Revisada'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('convertida', 'Convertida a pedido'),
    ]
    
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='cotizaciones',
        verbose_name="Cliente"
    )
    fecha_solicitud = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de solicitud")
    fecha_respuesta = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de respuesta")
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='pendiente',
        verbose_name="Estado"
    )
    notas_cliente = models.TextField(blank=True, verbose_name="Notas del cliente")
    notas_admin = models.TextField(blank=True, verbose_name="Notas del administrador")
    vigencia = models.IntegerField(default=15, verbose_name="Días de vigencia")
    
    class Meta:
        verbose_name = "Cotización"
        verbose_name_plural = "Cotizaciones"
        ordering = ['-fecha_solicitud']
        
    def __str__(self):
        return f"Cotización #{self.id} - {self.cliente.get_full_name()}"
        
    @property
    def total(self):
        """Calcula el total de la cotización sumando todos los items"""
        return sum(item.subtotal for item in self.items.all())
        
    @property
    def num_items(self):
        """Devuelve el número de items en la cotización"""
        return self.items.count()
    
class DetalleCotizacion(models.Model):
    cotizacion = models.ForeignKey(
        Cotizacion, 
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name="Cotización"
    )
    producto = models.ForeignKey(
        Producto, 
        on_delete=models.PROTECT,
        verbose_name="Producto"
    )
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    precio_unitario = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        verbose_name="Precio unitario"
    )
    notas = models.CharField(max_length=255, blank=True, verbose_name="Notas específicas")
    
    class Meta:
        verbose_name = "Detalle de cotización"
        verbose_name_plural = "Detalles de cotización"
        
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
        
    @property
    def subtotal(self):
        """Calcula el subtotal del item (precio x cantidad)"""
        if self.precio_unitario:
            return self.precio_unitario * self.cantidad
        # Si no hay precio establecido, usa el precio del producto
        return self.producto.precio * self.cantidad