"""
Signals para capturar automáticamente cambios en modelos y registrarlos en auditoría.
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.core.serializers import serialize
import json

from .models import (
    AuditLog, 
    HistorialProducto, 
    HistorialPedido, 
    HistorialCotizacion,
    HistorialFactura,
    HistorialCliente,
    HistorialCategoria
)
from inventario.models import Producto, Categoria
from pedidos.models import Pedido, Cliente
from cotizaciones.models import Cotizacion
from ventas.models import Factura


# Diccionario para almacenar los estados anteriores de los objetos
_pre_save_instances = {}


def get_current_user():
    """
    Obtiene el usuario actual del contexto de la solicitud.
    Esto requiere un middleware personalizado para almacenar el usuario en el thread local.
    """
    from threading import current_thread
    
    thread = current_thread()
    if hasattr(thread, 'user'):
        return thread.user
    return None


def get_field_changes(old_instance, new_instance):
    """
    Compara dos instancias y devuelve un diccionario con los cambios.
    """
    changes = {}
    
    if old_instance is None:
        return changes
    
    for field in new_instance._meta.fields:
        field_name = field.name
        
        # Ignorar campos de auditoría
        if field_name in ['id', 'fecha_creacion', 'fecha_actualizacion']:
            continue
        
        old_value = getattr(old_instance, field_name, None)
        new_value = getattr(new_instance, field_name, None)
        
        # Convertir a string para comparación
        old_str = str(old_value) if old_value is not None else None
        new_str = str(new_value) if new_value is not None else None
        
        if old_str != new_str:
            changes[field_name] = {
                'anterior': old_str,
                'nuevo': new_str
            }
    
    return changes


@receiver(pre_save)
def store_pre_save_instance(sender, instance, **kwargs):
    """
    Guarda el estado anterior del objeto antes de guardarlo.
    """
    # Solo para modelos que queremos auditar
    if sender._meta.app_label in ['inventario', 'pedidos', 'cotizaciones', 'ventas']:
        if instance.pk:
            try:
                old_instance = sender.objects.get(pk=instance.pk)
                key = f"{sender._meta.label}_{instance.pk}"
                _pre_save_instances[key] = old_instance
            except sender.DoesNotExist:
                pass


@receiver(post_save)
def create_audit_log(sender, instance, created, **kwargs):
    """
    Crea un registro de auditoría después de guardar un objeto.
    """
    # Evitar auditoría de modelos de auditoría (evitar recursión)
    if sender._meta.app_label == 'auditorias':
        return
    
    # Solo auditar ciertos modelos
    if sender._meta.app_label not in ['inventario', 'pedidos', 'cotizaciones', 'ventas', 'usuarios']:
        return
    
    try:
        usuario = get_current_user()
        usuario_nombre = usuario.get_full_name() or usuario.username if usuario else "Sistema"
        
        # Obtener el estado anterior si existe
        key = f"{sender._meta.label}_{instance.pk}"
        old_instance = _pre_save_instances.pop(key, None)
        
        # Determinar la acción
        if created:
            accion = AuditLog.ACTION_CREATE
            cambios = {}
        else:
            accion = AuditLog.ACTION_UPDATE
            cambios = get_field_changes(old_instance, instance)
        
        # Crear el registro de auditoría
        content_type = ContentType.objects.get_for_model(sender)
        
        AuditLog.objects.create(
            usuario=usuario,
            usuario_nombre=usuario_nombre,
            accion=accion,
            content_type=content_type,
            object_id=instance.pk,
            modelo=sender._meta.verbose_name,
            objeto_repr=str(instance),
            cambios=cambios
        )
        
        # Crear registros de historial específicos
        create_specific_history(sender, instance, created, old_instance, usuario)
        
    except Exception as e:
        # No interrumpir el flujo si falla la auditoría
        print(f"Error en auditoría: {e}")


@receiver(post_delete)
def create_delete_audit_log(sender, instance, **kwargs):
    """
    Crea un registro de auditoría después de eliminar un objeto.
    """
    # Evitar auditoría de modelos de auditoría
    if sender._meta.app_label == 'auditorias':
        return
    
    # Solo auditar ciertos modelos
    if sender._meta.app_label not in ['inventario', 'pedidos', 'cotizaciones', 'ventas', 'usuarios']:
        return
    
    try:
        usuario = get_current_user()
        usuario_nombre = usuario.get_full_name() or usuario.username if usuario else "Sistema"
        
        content_type = ContentType.objects.get_for_model(sender)
        
        AuditLog.objects.create(
            usuario=usuario,
            usuario_nombre=usuario_nombre,
            accion=AuditLog.ACTION_DELETE,
            content_type=content_type,
            object_id=instance.pk,
            modelo=sender._meta.verbose_name,
            objeto_repr=str(instance),
            cambios={}
        )
        
    except Exception as e:
        print(f"Error en auditoría de eliminación: {e}")


def create_specific_history(sender, instance, created, old_instance, usuario):
    """
    Crea registros de historial específicos para cada tipo de modelo.
    """
    try:
        # Historial de Producto
        if sender == Producto:
            if not created and old_instance:
                cambios = []
                if old_instance.nombre != instance.nombre:
                    cambios.append(f"Nombre: {old_instance.nombre} → {instance.nombre}")
                if old_instance.precio != instance.precio:
                    cambios.append(f"Precio: ${old_instance.precio} → ${instance.precio}")
                if old_instance.stock != instance.stock:
                    cambios.append(f"Stock: {old_instance.stock} → {instance.stock}")
                
                if cambios:
                    HistorialProducto.objects.create(
                        producto=instance,
                        usuario=usuario,
                        nombre_anterior=old_instance.nombre,
                        nombre_nuevo=instance.nombre,
                        precio_anterior=old_instance.precio,
                        precio_nuevo=instance.precio,
                        stock_anterior=old_instance.stock,
                        stock_nuevo=instance.stock,
                        descripcion="; ".join(cambios)
                    )
            elif created:
                HistorialProducto.objects.create(
                    producto=instance,
                    usuario=usuario,
                    nombre_nuevo=instance.nombre,
                    precio_nuevo=instance.precio,
                    stock_nuevo=instance.stock,
                    descripcion=f"Producto creado: {instance.nombre}"
                )
        
        # Historial de Pedido
        elif sender == Pedido:
            if not created and old_instance:
                if old_instance.estado != instance.estado:
                    HistorialPedido.objects.create(
                        pedido=instance,
                        usuario=usuario,
                        estado_anterior=old_instance.estado,
                        estado_nuevo=instance.estado,
                        descripcion=f"Estado cambiado de {old_instance.get_estado_display()} a {instance.get_estado_display()}"
                    )
            elif created:
                HistorialPedido.objects.create(
                    pedido=instance,
                    usuario=usuario,
                    estado_nuevo=instance.estado,
                    descripcion=f"Pedido creado en estado {instance.get_estado_display()}"
                )
        
        # Historial de Cotización
        elif sender == Cotizacion:
            if not created and old_instance:
                cambios = []
                if old_instance.estado != instance.estado:
                    cambios.append(f"Estado: {old_instance.get_estado_display()} → {instance.get_estado_display()}")
                if old_instance.total != instance.total:
                    cambios.append(f"Total: ${old_instance.total} → ${instance.total}")
                
                if cambios:
                    HistorialCotizacion.objects.create(
                        cotizacion=instance,
                        usuario=usuario,
                        estado_anterior=old_instance.estado,
                        estado_nuevo=instance.estado,
                        total_anterior=old_instance.total,
                        total_nuevo=instance.total,
                        descripcion="; ".join(cambios)
                    )
            elif created:
                HistorialCotizacion.objects.create(
                    cotizacion=instance,
                    usuario=usuario,
                    estado_nuevo=instance.estado,
                    total_nuevo=instance.total,
                    descripcion=f"Cotización creada con total ${instance.total}"
                )
        
        # Historial de Factura
        elif sender == Factura:
            if not created and old_instance:
                cambios = []
                if old_instance.estado != instance.estado:
                    cambios.append(f"Estado: {old_instance.get_estado_display()} → {instance.get_estado_display()}")
                if old_instance.total != instance.total:
                    cambios.append(f"Total: ${old_instance.total} → ${instance.total}")
                
                if cambios:
                    HistorialFactura.objects.create(
                        factura=instance,
                        usuario=usuario,
                        estado_anterior=old_instance.estado,
                        estado_nuevo=instance.estado,
                        total_anterior=old_instance.total,
                        total_nuevo=instance.total,
                        descripcion="; ".join(cambios)
                    )
            elif created:
                HistorialFactura.objects.create(
                    factura=instance,
                    usuario=usuario,
                    estado_nuevo=instance.estado,
                    total_nuevo=instance.total,
                    descripcion=f"Factura {instance.numero} creada con total ${instance.total}"
                )
        
        # Historial de Cliente
        elif sender == Cliente:
            if not created and old_instance:
                cambios = get_field_changes(old_instance, instance)
                if cambios:
                    descripcion = "Cliente actualizado: " + ", ".join([f"{k}: {v['anterior']} → {v['nuevo']}" for k, v in cambios.items()])
                    HistorialCliente.objects.create(
                        cliente=instance,
                        usuario=usuario,
                        cambios=cambios,
                        descripcion=descripcion
                    )
            elif created:
                HistorialCliente.objects.create(
                    cliente=instance,
                    usuario=usuario,
                    cambios={},
                    descripcion=f"Cliente creado: {instance.nombre} {instance.apellido}"
                )
        
        # Historial de Categoría
        elif sender == Categoria:
            if not created and old_instance:
                if old_instance.nombre != instance.nombre:
                    HistorialCategoria.objects.create(
                        categoria=instance,
                        usuario=usuario,
                        nombre_anterior=old_instance.nombre,
                        nombre_nuevo=instance.nombre,
                        descripcion=f"Nombre cambiado de '{old_instance.nombre}' a '{instance.nombre}'"
                    )
            elif created:
                HistorialCategoria.objects.create(
                    categoria=instance,
                    usuario=usuario,
                    nombre_nuevo=instance.nombre,
                    descripcion=f"Categoría creada: {instance.nombre}"
                )
                
    except Exception as e:
        print(f"Error creando historial específico: {e}")
