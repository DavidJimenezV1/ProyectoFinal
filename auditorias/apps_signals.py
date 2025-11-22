"""
Signals para registrar automáticamente cambios en auditorías.
Conecta con los modelos de todas las apps.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from auditorias.models import (
    AuditLog, HistorialProducto, HistorialPedido,
    HistorialCotizacion, HistorialFactura, HistorialCliente, HistorialCategoria
)

# ==================== MIDDLEWARE PARA CAPTURAR USUARIO ====================

_thread_locals = {}

def obtener_usuario_actual():
    """Obtiene el usuario actual de la request"""
    usuario = _thread_locals.get('user', None)
    return usuario

def establecer_usuario_actual(user):
    """Establece el usuario actual"""
    _thread_locals['user'] = user

# ==================== INVENTARIO ====================

@receiver(post_save, sender='inventario.Producto', dispatch_uid='registrar_cambio_producto')
def registrar_cambio_producto(sender, instance, created, **kwargs):
    """Registra cuando se crea o actualiza un producto"""
    usuario = obtener_usuario_actual()
    if not usuario:
        return
    
    accion = 'CREATE' if created else 'UPDATE'
    
    try:
        # Texto correcto en español
        if accion == 'CREATE':
            descripcion = f"Creación de producto: {instance.nombre}"
        else:
            descripcion = f"Actualización de producto: {instance.nombre}"
        
        audit_log = AuditLog.objects.create(
            usuario=usuario,
            accion=accion,
            modelo='Producto',
            objeto_id=instance.id,
            objeto_nombre=f"{instance.codigo} - {instance.nombre}",
            descripcion=descripcion
        )
        
        if accion == 'UPDATE':
            HistorialProducto.objects.create(
                audit_log=audit_log,
                producto_id=instance.id,
                precio_nuevo=instance.precio,
                stock_nuevo=instance.stock,
                estado_nuevo='actualizado'
            )
    except Exception as e:
        print(f"Error registrando producto: {e}")


@receiver(post_delete, sender='inventario.Producto', dispatch_uid='registrar_eliminacion_producto')
def registrar_eliminacion_producto(sender, instance, **kwargs):
    """Registra cuando se elimina un producto"""
    usuario = obtener_usuario_actual()
    if not usuario:
        return
    
    try:
        audit_log = AuditLog.objects.create(
            usuario=usuario,
            accion='DELETE',
            modelo='Producto',
            objeto_id=instance.id,
            objeto_nombre=f"{instance.codigo} - {instance.nombre}",
            descripcion=f"Eliminación de producto: {instance.nombre}"
        )
        
        HistorialProducto.objects.create(
            audit_log=audit_log,
            producto_id=instance.id,
            estado_nuevo='eliminado'
        )
    except Exception as e:
        print(f"Error registrando eliminación de producto: {e}")


@receiver(post_save, sender='inventario.Categoria', dispatch_uid='registrar_cambio_categoria')
def registrar_cambio_categoria(sender, instance, created, **kwargs):
    """Registra cuando se crea o actualiza una categoría"""
    usuario = obtener_usuario_actual()
    if not usuario:
        return
    
    accion = 'CREATE' if created else 'UPDATE'
    
    try:
        if accion == 'CREATE':
            descripcion = f"Creación de categoría: {instance.nombre}"
        else:
            descripcion = f"Actualización de categoría: {instance.nombre}"
        
        audit_log = AuditLog.objects.create(
            usuario=usuario,
            accion=accion,
            modelo='Categoria',
            objeto_id=instance.id,
            objeto_nombre=instance.nombre,
            descripcion=descripcion
        )
        
        HistorialCategoria.objects.create(
            audit_log=audit_log,
            categoria_id=instance.id,
            nombre_nuevo=instance.nombre,
            descripcion_nueva=instance.descripcion or ''
        )
    except Exception as e:
        print(f"Error registrando categoría: {e}")


@receiver(post_save, sender='pedidos.Pedido', dispatch_uid='registrar_cambio_pedido')
def registrar_cambio_pedido(sender, instance, created, **kwargs):
    """Registra cuando se crea o actualiza un pedido"""
    usuario = obtener_usuario_actual()
    if not usuario:
        return
    
    accion = 'CREATE' if created else 'UPDATE'
    
    try:
        if accion == 'CREATE':
            descripcion = f"Creación de pedido: Pedido #{instance.id}"
        else:
            descripcion = f"Actualización de pedido: Pedido #{instance.id}"
        
        audit_log = AuditLog.objects.create(
            usuario=usuario,
            accion=accion,
            modelo='Pedido',
            objeto_id=instance.id,
            objeto_nombre=f"Pedido #{instance.id}",
            descripcion=descripcion
        )
        
        if accion == 'UPDATE':
            HistorialPedido.objects.create(
                audit_log=audit_log,
                pedido_id=instance.id,
                estado_nuevo=instance.estado,
                cliente_nuevo=str(instance.cliente)
            )
    except Exception as e:
        print(f"Error registrando pedido: {e}")


@receiver(post_delete, sender='pedidos.Pedido', dispatch_uid='registrar_eliminacion_pedido')
def registrar_eliminacion_pedido(sender, instance, **kwargs):
    """Registra cuando se elimina un pedido"""
    usuario = obtener_usuario_actual()
    if not usuario:
        return
    
    try:
        audit_log = AuditLog.objects.create(
            usuario=usuario,
            accion='DELETE',
            modelo='Pedido',
            objeto_id=instance.id,
            objeto_nombre=f"Pedido #{instance.id}",
            descripcion=f"Eliminación de pedido: Pedido #{instance.id}"
        )
        
        HistorialPedido.objects.create(
            audit_log=audit_log,
            pedido_id=instance.id,
            estado_nuevo='eliminado'
        )
    except Exception as e:
        print(f"Error registrando eliminación de pedido: {e}")


@receiver(post_save, sender='cotizaciones.Cotizacion', dispatch_uid='registrar_cambio_cotizacion')
def registrar_cambio_cotizacion(sender, instance, created, **kwargs):
    """Registra cuando se crea o actualiza una cotización"""
    usuario = obtener_usuario_actual()
    if not usuario:
        return
    
    accion = 'CREATE' if created else 'UPDATE'
    
    try:
        if accion == 'CREATE':
            descripcion = f"Creación de cotización: Cotización #{instance.id}"
        else:
            descripcion = f"Actualización de cotización: Cotización #{instance.id}"
        
        audit_log = AuditLog.objects.create(
            usuario=usuario,
            accion=accion,
            modelo='Cotizacion',
            objeto_id=instance.id,
            objeto_nombre=f"Cotización #{instance.id}",
            descripcion=descripcion
        )
        
        if accion == 'UPDATE':
            HistorialCotizacion.objects.create(
                audit_log=audit_log,
                cotizacion_id=instance.id,
                estado_nuevo=instance.estado,
                monto_nuevo=instance.total
            )
    except Exception as e:
        print(f"Error registrando cotización: {e}")


@receiver(post_delete, sender='cotizaciones.Cotizacion', dispatch_uid='registrar_eliminacion_cotizacion')
def registrar_eliminacion_cotizacion(sender, instance, **kwargs):
    """Registra cuando se elimina una cotización"""
    usuario = obtener_usuario_actual()
    if not usuario:
        return
    
    try:
        audit_log = AuditLog.objects.create(
            usuario=usuario,
            accion='DELETE',
            modelo='Cotizacion',
            objeto_id=instance.id,
            objeto_nombre=f"Cotización #{instance.id}",
            descripcion=f"Eliminación de cotización: Cotización #{instance.id}"
        )
        
        HistorialCotizacion.objects.create(
            audit_log=audit_log,
            cotizacion_id=instance.id,
            estado_nuevo='eliminada'
        )
    except Exception as e:
        print(f"Error registrando eliminación de cotización: {e}")


@receiver(post_save, sender='ventas.Factura', dispatch_uid='registrar_cambio_factura')
def registrar_cambio_factura(sender, instance, created, **kwargs):
    """Registra cuando se crea o actualiza una factura"""
    usuario = obtener_usuario_actual()
    if not usuario:
        return
    
    accion = 'CREATE' if created else 'UPDATE'
    
    try:
        if accion == 'CREATE':
            descripcion = f"Creación de factura: {instance.numero}"
        else:
            descripcion = f"Actualización de factura: {instance.numero}"
        
        audit_log = AuditLog.objects.create(
            usuario=usuario,
            accion=accion,
            modelo='Factura',
            objeto_id=instance.id,
            objeto_nombre=f"Factura #{instance.numero}",
            descripcion=descripcion
        )
        
        if accion == 'UPDATE':
            HistorialFactura.objects.create(
                audit_log=audit_log,
                factura_id=instance.id,
                estado_nuevo=instance.estado,
                monto_nuevo=instance.total
            )
    except Exception as e:
        print(f"Error registrando factura: {e}")


@receiver(post_delete, sender='ventas.Factura', dispatch_uid='registrar_eliminacion_factura')
def registrar_eliminacion_factura(sender, instance, **kwargs):
    """Registra cuando se elimina una factura"""
    usuario = obtener_usuario_actual()
    if not usuario:
        return
    
    try:
        audit_log = AuditLog.objects.create(
            usuario=usuario,
            accion='DELETE',
            modelo='Factura',
            objeto_id=instance.id,
            objeto_nombre=f"Factura #{instance.numero}",
            descripcion=f"Eliminación de factura: {instance.numero}"
        )
        
        HistorialFactura.objects.create(
            audit_log=audit_log,
            factura_id=instance.id,
            estado_nuevo='eliminada'
        )
    except Exception as e:
        print(f"Error registrando eliminación de factura: {e}")