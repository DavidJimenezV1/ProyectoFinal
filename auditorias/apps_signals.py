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

def get_current_user():
    """Obtiene el usuario actual de la request"""
    usuario = _thread_locals.get('user', None)
    return usuario

def set_current_user(user):
    """Establece el usuario actual"""
    _thread_locals['user'] = user

# ==================== INVENTARIO ====================

@receiver(post_save, sender='inventario.Producto', dispatch_uid='registrar_cambio_producto')
def registrar_cambio_producto(sender, instance, created, **kwargs):
    """Registra cuando se crea o actualiza un producto"""
    usuario = get_current_user()
    if not usuario:
        return
    
    accion = 'CREATE' if created else 'UPDATE'
    
    try:
        audit_log = AuditLog.objects.create(
            usuario=usuario,
            accion=accion,
            modelo='Producto',
            objeto_id=instance.id,
            objeto_nombre=f"{instance.codigo} - {instance.nombre}",
            descripcion=f"{accion} de producto: {instance.nombre}"
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
    usuario = get_current_user()
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
    usuario = get_current_user()
    if not usuario:
        return
    
    accion = 'CREATE' if created else 'UPDATE'
    
    try:
        audit_log = AuditLog.objects.create(
            usuario=usuario,
            accion=accion,
            modelo='Categoria',
            objeto_id=instance.id,
            objeto_nombre=instance.nombre,
            descripcion=f"{accion} de categoría: {instance.nombre}"
        )
        
        HistorialCategoria.objects.create(
            audit_log=audit_log,
            categoria_id=instance.id,
            nombre_nuevo=instance.nombre,
            descripcion_nueva=instance.descripcion or ''
        )
    except Exception as e:
        print(f"Error registrando categoría: {e}")


# ==================== PEDIDOS ====================

@receiver(post_save, sender='pedidos.Pedido', dispatch_uid='registrar_cambio_pedido')
def registrar_cambio_pedido(sender, instance, created, **kwargs):
    """Registra cuando se crea o actualiza un pedido"""
    usuario = get_current_user()
    if not usuario:
        return
    
    accion = 'CREATE' if created else 'UPDATE'
    
    try:
        audit_log = AuditLog.objects.create(
            usuario=usuario,
            accion=accion,
            modelo='Pedido',
            objeto_id=instance.id,
            objeto_nombre=f"Pedido #{instance.id}",
            descripcion=f"{accion} de pedido #{instance.id}"
        )
        
        HistorialPedido.objects.create(
            audit_log=audit_log,
            pedido_id=instance.id,
            estado_nuevo=instance.estado,
            cliente_nuevo=f"{instance.cliente.nombre} {instance.cliente.apellido}" if instance.cliente else "Sin cliente"
        )
    except Exception as e:
        print(f"Error registrando pedido: {e}")


@receiver(post_delete, sender='pedidos.Pedido', dispatch_uid='registrar_eliminacion_pedido')
def registrar_eliminacion_pedido(sender, instance, **kwargs):
    """Registra cuando se elimina un pedido"""
    usuario = get_current_user()
    if not usuario:
        return
    
    try:
        audit_log = AuditLog.objects.create(
            usuario=usuario,
            accion='DELETE',
            modelo='Pedido',
            objeto_id=instance.id,
            objeto_nombre=f"Pedido #{instance.id}",
            descripcion=f"Eliminación de pedido #{instance.id}"
        )
        
        HistorialPedido.objects.create(
            audit_log=audit_log,
            pedido_id=instance.id,
            estado_nuevo='eliminado'
        )
    except Exception as e:
        print(f"Error registrando eliminación de pedido: {e}")


@receiver(post_save, sender='pedidos.Cliente', dispatch_uid='registrar_cambio_cliente')
def registrar_cambio_cliente(sender, instance, created, **kwargs):
    """Registra cuando se crea o actualiza un cliente"""
    usuario = get_current_user()
    if not usuario:
        return
    
    accion = 'CREATE' if created else 'UPDATE'
    
    try:
        audit_log = AuditLog.objects.create(
            usuario=usuario,
            accion=accion,
            modelo='Cliente',
            objeto_id=instance.id,
            objeto_nombre=f"{instance.nombre} {instance.apellido}",
            descripcion=f"{accion} de cliente: {instance.nombre} {instance.apellido}"
        )
        
        HistorialCliente.objects.create(
            audit_log=audit_log,
            cliente_id=instance.id,
            cambios={
                'nombre': instance.nombre,
                'email': instance.email,
                'telefono': instance.telefono
            }
        )
    except Exception as e:
        print(f"Error registrando cliente: {e}")


# ==================== COTIZACIONES ====================

@receiver(post_save, sender='cotizaciones.Cotizacion', dispatch_uid='registrar_cambio_cotizacion')
def registrar_cambio_cotizacion(sender, instance, created, **kwargs):
    """Registra cuando se crea o actualiza una cotización"""
    usuario = get_current_user()
    if not usuario:
        return
    
    accion = 'CREATE' if created else 'UPDATE'
    
    try:
        audit_log = AuditLog.objects.create(
            usuario=usuario,
            accion=accion,
            modelo='Cotizacion',
            objeto_id=instance.id,
            objeto_nombre=f"Cotización #{instance.id}",
            descripcion=f"{accion} de cotización #{instance.id}",
            datos_nuevos={'total': str(instance.total), 'estado': instance.estado}
        )
        
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
    usuario = get_current_user()
    if not usuario:
        return
    
    try:
        audit_log = AuditLog.objects.create(
            usuario=usuario,
            accion='DELETE',
            modelo='Cotizacion',
            objeto_id=instance.id,
            objeto_nombre=f"Cotización #{instance.id}",
            descripcion=f"Eliminación de cotización #{instance.id}"
        )
        
        HistorialCotizacion.objects.create(
            audit_log=audit_log,
            cotizacion_id=instance.id,
            estado_nuevo='eliminado'
        )
    except Exception as e:
        print(f"Error registrando eliminación de cotización: {e}")


# ==================== DETALLES DE COTIZACIONES ====================

@receiver(post_save, sender='cotizaciones.DetalleCotizacion', dispatch_uid='registrar_cambio_detalle_cotizacion')
def registrar_cambio_detalle_cotizacion(sender, instance, created, **kwargs):
    """Registra cuando se agrega o actualiza un producto en una cotización"""
    usuario = get_current_user()
    if not usuario:
        return
    
    accion = 'CREATE' if created else 'UPDATE'
    
    try:
        descripcion = f"{accion} de producto en cotización #{instance.cotizacion.id}: {instance.producto.nombre} (x{instance.cantidad})"
        
        audit_log = AuditLog.objects.create(
            usuario=usuario,
            accion=accion,
            modelo='Cotizacion',
            objeto_id=instance.cotizacion.id,
            objeto_nombre=f"Cotización #{instance.cotizacion.id}",
            descripcion=descripcion,
            datos_nuevos={
                'producto': instance.producto.nombre,
                'cantidad': instance.cantidad,
                'precio_unitario': str(instance.precio_unitario or instance.producto.precio),
                'subtotal': str(instance.subtotal)
            }
        )
        
        HistorialCotizacion.objects.create(
            audit_log=audit_log,
            cotizacion_id=instance.cotizacion.id,
            estado_nuevo=instance.cotizacion.estado,
            monto_nuevo=instance.cotizacion.total
        )
    except Exception as e:
        print(f"Error registrando detalle de cotización: {e}")


@receiver(post_delete, sender='cotizaciones.DetalleCotizacion', dispatch_uid='registrar_eliminacion_detalle_cotizacion')
def registrar_eliminacion_detalle_cotizacion(sender, instance, **kwargs):
    """Registra cuando se elimina un producto de una cotización"""
    usuario = get_current_user()
    if not usuario:
        return
    
    try:
        descripcion = f"Eliminación de producto en cotización #{instance.cotizacion.id}: {instance.producto.nombre}"
        
        audit_log = AuditLog.objects.create(
            usuario=usuario,
            accion='DELETE',
            modelo='Cotizacion',
            objeto_id=instance.cotizacion.id,
            objeto_nombre=f"Cotización #{instance.cotizacion.id}",
            descripcion=descripcion
        )
        
        HistorialCotizacion.objects.create(
            audit_log=audit_log,
            cotizacion_id=instance.cotizacion.id,
            estado_nuevo=instance.cotizacion.estado,
            monto_nuevo=instance.cotizacion.total
        )
    except Exception as e:
        print(f"Error registrando eliminación de detalle de cotización: {e}")


# ==================== VENTAS / FACTURAS ====================

@receiver(post_save, sender='ventas.Factura', dispatch_uid='registrar_cambio_factura')
def registrar_cambio_factura(sender, instance, created, **kwargs):
    """Registra cuando se crea o actualiza una factura"""
    usuario = get_current_user()
    if not usuario:
        return
    
    accion = 'CREATE' if created else 'UPDATE'
    
    try:
        audit_log = AuditLog.objects.create(
            usuario=usuario,
            accion=accion,
            modelo='Factura',
            objeto_id=instance.id,
            objeto_nombre=f"Factura #{instance.numero}",
            descripcion=f"{accion} de factura: {instance.numero}",
            datos_nuevos={'total': str(instance.total), 'estado': instance.estado}
        )
        
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
    usuario = get_current_user()
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
            estado_nuevo='eliminado'
        )
    except Exception as e:
        print(f"Error registrando eliminación de factura: {e}")