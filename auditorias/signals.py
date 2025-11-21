from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from auditorias.models import AuditLog
import json

def get_client_ip(request):
    """Obtener IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def registrar_auditoria(usuario, accion, modelo, objeto_id, objeto_nombre, 
                       datos_anteriores=None, datos_nuevos=None, ip=None, descripcion=""):
    """Función auxiliar para registrar acciones en la auditoría"""
    
    cambios_resumidos = {}
    if datos_anteriores and datos_nuevos:
        for key in datos_nuevos:
            if datos_anteriores.get(key) != datos_nuevos.get(key):
                cambios_resumidos[key] = {
                    'anterior': str(datos_anteriores.get(key)),
                    'nuevo': str(datos_nuevos.get(key))
                }
    
    AuditLog.objects.create(
        usuario=usuario,
        accion=accion,
        modelo=modelo,
        objeto_id=objeto_id,
        objeto_nombre=objeto_nombre,
        datos_anteriores=datos_anteriores,
        datos_nuevos=datos_nuevos,
        ip_address=ip,
        descripcion=descripcion or f"{accion} en {modelo} (ID: {objeto_id})",
        cambios_resumidos=cambios_resumidos
    )