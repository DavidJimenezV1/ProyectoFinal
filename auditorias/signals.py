from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Auditoria
import json


def obtener_usuario_actual(instance):
    """
    Intenta obtener el usuario actual del contexto de la instancia.
    Retorna None si no está disponible.
    """
    if hasattr(instance, '_current_user'):
        return instance._current_user
    return None


def obtener_ip_actual(instance):
    """
    Intenta obtener la IP actual del contexto de la instancia.
    Retorna None si no está disponible.
    """
    if hasattr(instance, '_current_ip'):
        return instance._current_ip
    return None


def obtener_cambios(instance, campos_excluir=None):
    """
    Obtiene los cambios realizados en una instancia comparando con su estado anterior.
    """
    if campos_excluir is None:
        campos_excluir = ['fecha_actualizacion', 'fecha_creacion', 'updated_at', 'created_at']
    
    if not hasattr(instance, '_state_antes'):
        return {}
    
    cambios = {}
    for field in instance._meta.fields:
        if field.name in campos_excluir:
            continue
        
        valor_actual = getattr(instance, field.name)
        valor_anterior = instance._state_antes.get(field.name)
        
        # Convertir valores a string para comparación
        valor_actual_str = str(valor_actual) if valor_actual is not None else None
        valor_anterior_str = str(valor_anterior) if valor_anterior is not None else None
        
        if valor_actual_str != valor_anterior_str:
            cambios[field.verbose_name or field.name] = {
                'anterior': valor_anterior_str,
                'nuevo': valor_actual_str
            }
    
    return cambios


def guardar_estado_anterior(sender, instance, **kwargs):
    """
    Guarda el estado anterior de una instancia antes de que se actualice.
    """
    if instance.pk:  # Solo para actualizaciones
        try:
            instancia_anterior = sender.objects.get(pk=instance.pk)
            instance._state_antes = {}
            for field in instance._meta.fields:
                instance._state_antes[field.name] = getattr(instancia_anterior, field.name)
        except sender.DoesNotExist:
            instance._state_antes = {}


def registrar_auditoria_creacion(sender, instance, created, **kwargs):
    """
    Registra la creación de un nuevo objeto.
    """
    if created:
        Auditoria.objects.create(
            usuario=obtener_usuario_actual(instance),
            accion='CREATE',
            content_type=ContentType.objects.get_for_model(sender),
            object_id=instance.pk,
            objeto_repr=str(instance),
            cambios={},
            ip_address=obtener_ip_actual(instance)
        )


def registrar_auditoria_actualizacion(sender, instance, created, **kwargs):
    """
    Registra la actualización de un objeto existente.
    """
    if not created and hasattr(instance, '_state_antes'):
        cambios = obtener_cambios(instance)
        if cambios:  # Solo registrar si hay cambios
            Auditoria.objects.create(
                usuario=obtener_usuario_actual(instance),
                accion='UPDATE',
                content_type=ContentType.objects.get_for_model(sender),
                object_id=instance.pk,
                objeto_repr=str(instance),
                cambios=cambios,
                ip_address=obtener_ip_actual(instance)
            )


def registrar_auditoria_eliminacion(sender, instance, **kwargs):
    """
    Registra la eliminación de un objeto.
    """
    Auditoria.objects.create(
        usuario=obtener_usuario_actual(instance),
        accion='DELETE',
        content_type=ContentType.objects.get_for_model(sender),
        object_id=instance.pk,
        objeto_repr=str(instance),
        cambios={},
        ip_address=obtener_ip_actual(instance)
    )


def conectar_signals_modelo(modelo):
    """
    Conecta todos los signals necesarios para un modelo específico.
    """
    # Pre-save para guardar el estado anterior
    pre_save.connect(guardar_estado_anterior, sender=modelo, weak=False)
    
    # Post-save para registrar creaciones y actualizaciones
    post_save.connect(registrar_auditoria_creacion, sender=modelo, weak=False)
    post_save.connect(registrar_auditoria_actualizacion, sender=modelo, weak=False)
    
    # Post-delete para registrar eliminaciones
    post_delete.connect(registrar_auditoria_eliminacion, sender=modelo, weak=False)
