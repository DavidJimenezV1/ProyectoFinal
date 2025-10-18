from django.db import models
from decimal import Decimal
from django.utils import timezone
from inventario.models import Producto
from usuarios.models import Usuario

class Factura(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagada', 'Pagada'),
        ('cancelada', 'Cancelada'),
    ]
    
    numero = models.CharField(max_length=20, unique=True, verbose_name="Número de factura")
    fecha_emision = models.DateTimeField(default=timezone.now, verbose_name="Fecha de emisión")
    cliente = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='facturas')
    nombre_cliente = models.CharField(max_length=200, verbose_name="Nombre del cliente")
    documento_cliente = models.CharField(max_length=20, blank=True, verbose_name="Documento de identidad")
    direccion_cliente = models.CharField(max_length=255, blank=True, verbose_name="Dirección")
    telefono_cliente = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    email_cliente = models.EmailField(blank=True, verbose_name="Email")
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    con_iva = models.BooleanField(default=True, verbose_name="Aplicar IVA")
    porcentaje_iva = models.DecimalField(max_digits=5, decimal_places=2, default=19.00, verbose_name="Porcentaje IVA")
    valor_iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    notas = models.TextField(blank=True)
    vendedor = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='ventas_realizadas')
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        ordering = ['-fecha_emision']
    
    def __str__(self):
        return f"Factura #{self.numero} - {self.nombre_cliente}"
    
    def calcular_totales(self):
        """Calcula el subtotal, IVA y total de la factura"""
        # Recalcula subtotal basado en los items
        self.subtotal = sum(item.subtotal for item in self.items.all())
        
        # Calcula el IVA si corresponde
        if self.con_iva:
            self.valor_iva = self.subtotal * (self.porcentaje_iva / Decimal('100'))
        else:
            self.valor_iva = Decimal('0')
            
        # Calcula el total
        self.total = self.subtotal + self.valor_iva
        
        # Guarda los cambios
        self.save()

    def generar_numero(self):
        """Genera un número de factura único"""
        ultimo = Factura.objects.order_by('-id').first()
        if ultimo:
            ultimo_numero = int(ultimo.numero.split('-')[-1])
            nuevo_numero = ultimo_numero + 1
        else:
            nuevo_numero = 1
            
        año_actual = timezone.now().year
        self.numero = f"TO-{año_actual}-{nuevo_numero:04d}"
        return self.numero

class ItemFactura(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = "Item de factura"
        verbose_name_plural = "Items de factura"
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
    
    def save(self, *args, **kwargs):
        # Calcular subtotal
        self.subtotal = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)
        
        # Actualizar totales de la factura
        self.factura.calcular_totales()
    
    def delete(self, *args, **kwargs):
        factura = self.factura
        super().delete(*args, **kwargs)
        # Recalcular totales de la factura
        factura.calcular_totales()