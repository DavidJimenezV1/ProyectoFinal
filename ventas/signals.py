from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ItemFactura, Factura

@receiver(post_save, sender=ItemFactura)
def actualizar_stock_al_guardar(sender, instance, created, **kwargs):
    """Reduce el stock cuando se crea o actualiza un item de factura"""
    if instance.factura.estado == 'pagada':  # Solo reducir stock en facturas pagadas
        producto = instance.producto
        
        if created:  # Si es un item nuevo
            # Reducir stock
            producto.stock -= instance.cantidad
        else:  # Si se está actualizando un item existente
            # Obtener el item anterior para ver cuánto stock hay que ajustar
            try:
                item_anterior = ItemFactura.objects.get(pk=instance.pk)
                diferencia = item_anterior.cantidad - instance.cantidad
                producto.stock += diferencia  # Si es negativo, reducirá el stock
            except:
                # Si no se puede obtener el item anterior, reducir por la cantidad completa
                producto.stock -= instance.cantidad
                
        # Guardar los cambios en el producto
        if producto.stock < 0:
            producto.stock = 0
        producto.save()

@receiver(post_delete, sender=ItemFactura)
def restaurar_stock_al_eliminar(sender, instance, **kwargs):
    """Restaura el stock cuando se elimina un item de factura"""
    if instance.factura.estado == 'pagada':
        producto = instance.producto
        producto.stock += instance.cantidad
        producto.save()

@receiver(post_save, sender=Factura)
def manejar_cambio_estado_factura(sender, instance, **kwargs):
    """Actualiza el stock cuando cambia el estado de una factura"""
    # Si la factura acaba de pasar a estado 'pagada'
    if instance.estado == 'pagada':
        for item in instance.items.all():
            producto = item.producto
            producto.stock -= item.cantidad
            if producto.stock < 0:
                producto.stock = 0
            producto.save()
    
    # Si la factura se cancela y estaba pagada previamente
    elif instance.estado == 'cancelada':
        try:
            factura_anterior = Factura.objects.get(pk=instance.pk)
            if factura_anterior.estado == 'pagada':
                # Restaurar el stock
                for item in instance.items.all():
                    producto = item.producto
                    producto.stock += item.cantidad
                    producto.save()
        except:
            pass