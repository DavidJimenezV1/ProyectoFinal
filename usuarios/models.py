from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    ADMIN = 'admin'
    CLIENTE = 'cliente'
    
    TIPOS_USUARIO = [
        (ADMIN, 'Administrador'),
        (CLIENTE, 'Cliente'),
    ]
    
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TIPOS_USUARIO,
        default=CLIENTE,
        verbose_name="Tipo de Usuario"
    )
    
    telefono = models.CharField(max_length=15, blank=True, null=True, verbose_name="Teléfono")
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección")
    empresa = models.CharField(max_length=100, blank=True, null=True, verbose_name="Empresa")
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        
    def __str__(self):
        return self.username
    
    @property
    def es_admin(self):
        return self.tipo_usuario == self.ADMIN
        
    @property
    def es_cliente(self):
        return self.tipo_usuario == self.CLIENTE