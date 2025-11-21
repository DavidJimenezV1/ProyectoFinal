from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import json

User = get_user_model()


class Auditoria(models.Model):
    """Modelo para registrar todas las acciones de auditoría en el sistema"""
    
    ACCION_CHOICES = [
        ('CREATE', 'Creación'),
        ('UPDATE', 'Actualización'),
        ('DELETE', 'Eliminación'),
    ]
    
    # Usuario que realizó la acción
    usuario = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Usuario"
    )
    
    # Tipo de acción
    accion = models.CharField(
        max_length=10, 
        choices=ACCION_CHOICES,
        verbose_name="Acción"
    )
    
    # Información del modelo afectado usando Generic Foreign Key
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE,
        verbose_name="Tipo de contenido"
    )
    object_id = models.PositiveIntegerField(verbose_name="ID del objeto")
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Detalles del cambio
    objeto_repr = models.CharField(
        max_length=200, 
        verbose_name="Representación del objeto"
    )
    cambios = models.JSONField(
        null=True, 
        blank=True,
        verbose_name="Cambios realizados"
    )
    
    # Metadatos
    fecha_hora = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y hora"
    )
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True,
        verbose_name="Dirección IP"
    )
    
    class Meta:
        verbose_name = "Auditoría"
        verbose_name_plural = "Auditorías"
        ordering = ['-fecha_hora']
        indexes = [
            models.Index(fields=['-fecha_hora']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['usuario']),
        ]
    
    def __str__(self):
        return f"{self.get_accion_display()} - {self.objeto_repr} - {self.fecha_hora.strftime('%Y-%m-%d %H:%M')}"
    
    def cambios_formateados(self):
        """Devuelve los cambios en formato legible"""
        if not self.cambios:
            return "Sin cambios registrados"
        
        try:
            if isinstance(self.cambios, str):
                cambios_dict = json.loads(self.cambios)
            else:
                cambios_dict = self.cambios
            
            resultado = []
            for campo, valores in cambios_dict.items():
                if isinstance(valores, dict) and 'anterior' in valores and 'nuevo' in valores:
                    resultado.append(f"{campo}: '{valores['anterior']}' → '{valores['nuevo']}'")
                else:
                    resultado.append(f"{campo}: {valores}")
            
            return "\n".join(resultado)
        except (json.JSONDecodeError, TypeError):
            return str(self.cambios)
