from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Usuario

class UsuarioAdmin(UserAdmin):
    list_display = ('username_colored', 'email_colored', 'first_name_colored', 'last_name_colored', 'tipo_usuario_colored')
    list_filter = ('tipo_usuario', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email', 'telefono', 'direccion', 'empresa')}),
        ('Permisos', {'fields': ('tipo_usuario', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'tipo_usuario', 'is_staff', 'is_active'),
        }),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    
    def username_colored(self, obj):
        """Muestra el nombre de usuario con fondo blanco y texto negro"""
        return format_html(
            '<div style="background-color: white !important; color: #000000 !important; padding: 8px 12px; border-radius: 4px; font-weight: bold;">{}</div>',
            obj.username
        )
    username_colored.short_description = "Nombre de Usuario"
    
    def email_colored(self, obj):
        """Muestra el email con fondo blanco y texto negro"""
        return format_html(
            '<div style="background-color: white !important; color: #000000 !important; padding: 8px 12px; border-radius: 4px;">{}</div>',
            obj.email
        )
    email_colored.short_description = "Dirección de Correo Electrónico"
    
    def first_name_colored(self, obj):
        """Muestra el nombre con fondo blanco y texto negro"""
        nombre = obj.first_name or "-"
        return format_html(
            '<div style="background-color: white !important; color: #000000 !important; padding: 8px 12px; border-radius: 4px;">{}</div>',
            nombre
        )
    first_name_colored.short_description = "Nombre"
    
    def last_name_colored(self, obj):
        """Muestra los apellidos con fondo blanco y texto negro"""
        apellidos = obj.last_name or "-"
        return format_html(
            '<div style="background-color: white !important; color: #000000 !important; padding: 8px 12px; border-radius: 4px;">{}</div>',
            apellidos
        )
    last_name_colored.short_description = "Apellidos"
    
    def tipo_usuario_colored(self, obj):
        """Muestra el tipo de usuario con badge de color"""
        colores = {
            'admin': '#dc3545',
            'cliente': '#28a745',
        }
        color = colores.get(obj.tipo_usuario, '#6c757d')
        return format_html(
            '<div style="background-color: {} !important; color: white !important; padding: 8px 12px; border-radius: 4px; font-weight: bold; text-align: center;">{}</div>',
            color, obj.get_tipo_usuario_display()
        )
    tipo_usuario_colored.short_description = "Tipo de Usuario"

admin.site.register(Usuario, UsuarioAdmin)