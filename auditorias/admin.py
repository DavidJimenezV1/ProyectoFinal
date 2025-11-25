from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Q
from core.utils import formato_pesos
from auditorias.models import (
    AuditLog, HistorialProducto, HistorialPedido,
    HistorialCotizacion, HistorialFactura, HistorialCliente, HistorialCategoria
)


# ==================== REGISTRO DE AUDITORÍA ====================

class AdminRegistroAuditoria(admin.ModelAdmin):
    """Admin personalizado para Registros de Auditoría"""
    list_display = ('resumen_corto', 'usuario_display', 'modelo_icon', 'fecha_hora_display', 'accion_color', 'descripcion_display')
    list_filter = ('accion', 'modelo', 'timestamp', 'usuario')
    search_fields = ('objeto_nombre', 'usuario__username', 'descripcion')
    readonly_fields = ('usuario', 'accion', 'modelo', 'objeto_id', 'objeto_nombre', 'timestamp', 'ip_address', 'descripcion', 'cambios_display', 'datos_anterior_display', 'datos_nuevo_display')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Información General', {
            'fields': ('usuario_display', 'accion_color', 'modelo_icon', 'fecha_hora_display')
        }),
        ('Objeto Modificado', {
            'fields': ('objeto_nombre', 'objeto_id')
        }),
        ('Detalles de Cambios', {
            'fields': ('cambios_display', 'datos_anterior_display', 'datos_nuevo_display'),
            'classes': ('collapse',)
        }),
        ('Información Técnica', {
            'fields': ('ip_address', 'descripcion'),
            'classes': ('collapse',)
        }),
    )
    
    def resumen_corto(self, obj):
        """Muestra un resumen corto del cambio - CON TEXTO BLANCO"""
        emojis = {
            'CREATE': '✅',
            'UPDATE': '🔄',
            'DELETE': '❌',
            'VIEW': '👁️'
        }
        emoji = emojis.get(obj.accion, '📝')
        return format_html(
            '<span style="color: #ffffff !important; font-weight: 900;">{} {}</span>',
            emoji, obj.objeto_nombre
        )
    resumen_corto.short_description = "Resumen"
    
    def usuario_display(self, obj):
        """Muestra el usuario de forma legible"""
        if obj.usuario:
            return f"👤 {obj.usuario.get_full_name() or obj.usuario.username}"
        return "Sistema"
    usuario_display.short_description = "Usuario"
    
    def modelo_icon(self, obj):
        """Muestra el modelo con icono"""
        iconos = {
            'Producto': '📦',
            'Pedido': '📋',
            'Cotizacion': '💬',
            'Factura': '🧾',
            'Cliente': '👥',
            'Categoria': '📂',
        }
        icon = iconos.get(obj.modelo, '📄')
        return f"{icon} {obj.modelo}"
    modelo_icon.short_description = "Modelo"
    
    def fecha_hora_display(self, obj):
        """Muestra la fecha/hora de forma legible"""
        return obj.timestamp.strftime("%d/%m/%Y %H:%M:%S")
    fecha_hora_display.short_description = "Fecha/Hora"
    
    def accion_color(self, obj):
        """Muestra la acción con color"""
        acciones_traduccion = {
            'CREATE': 'Crear',
            'UPDATE': 'Actualizar',
            'DELETE': 'Eliminar',
            'VIEW': 'Ver',
        }
        colores = {
            'CREATE': '#28a745',
            'UPDATE': '#ffc107',
            'DELETE': '#dc3545',
            'VIEW': '#17a2b8',
        }
        color = colores.get(obj.accion, '#6c757d')
        accion_traducida = acciones_traduccion.get(obj.accion, obj.get_accion_display())
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            accion_traducida
        )
    accion_color.short_description = "Acción"
    
    def descripcion_display(self, obj):
        """Muestra la descripción en la lista"""
        if obj.descripcion:
            descripcion = obj.descripcion[:80]
            if len(obj.descripcion) > 80:
                descripcion += "..."
            return descripcion
        return "-"
    descripcion_display.short_description = "Descripción"
    
    def cambios_display(self, obj):
        """Muestra los cambios de forma legible"""
        if not obj.cambios:
            return "Sin cambios específicos"
        
        html = '<table style="width: 100%; border-collapse: collapse;">'
        for campo, (antes, despues) in obj.cambios.items():
            html += f'''
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 8px; font-weight: bold; width: 30%;">{campo}</td>
                <td style="padding: 8px; background-color: #ffebee; color: #c62828;">❌ {antes}</td>
                <td style="padding: 8px; background-color: #e8f5e9; color: #2e7d32;">✅ {despues}</td>
            </tr>
            '''
        html += '</table>'
        return format_html(html)
    cambios_display.short_description = "Cambios Realizados"
    
    def datos_anterior_display(self, obj):
        """Muestra los datos anteriores en JSON formateado"""
        if not obj.datos_anterior:
            return "N/A"
        import json
        try:
            datos = json.dumps(obj.datos_anterior, indent=2, ensure_ascii=False)
            return format_html('<pre style="background: #f4f4f4; padding: 10px; border-radius: 3px;">{}</pre>', datos)
        except:
            return str(obj.datos_anterior)
    datos_anterior_display.short_description = "Estado Anterior"
    
    def datos_nuevo_display(self, obj):
        """Muestra los datos nuevos en JSON formateado"""
        if not obj.datos_nuevo:
            return "N/A"
        import json
        try:
            datos = json.dumps(obj.datos_nuevo, indent=2, ensure_ascii=False)
            return format_html('<pre style="background: #f4f4f4; padding: 10px; border-radius: 3px;">{}</pre>', datos)
        except:
            return str(obj.datos_nuevo)
    datos_nuevo_display.short_description = "Estado Nuevo"
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# ==================== HISTORIAL PRODUCTO ====================

class AdminHistorialProducto(admin.ModelAdmin):
    list_display = ('producto_id_display', 'usuario_display', 'accion_display', 'precio_cambio', 'stock_cambio', 'descripcion_display', 'fecha_hora_display')
    list_filter = ('audit_log__accion', 'audit_log__timestamp', 'audit_log__usuario')
    readonly_fields = ('audit_log', 'producto_id', 'precio_display', 'stock_display', 'descripcion_completa', 'fecha_hora_display')
    
    def producto_id_display(self, obj):
        """Muestra el ID del producto en BLANCO"""
        return format_html(
            '<span style="color: #ffffff !important; font-weight: 900;">{}</span>',
            obj.producto_id
        )
    producto_id_display.short_description = "Producto ID"
    
    def usuario_display(self, obj):
        if obj.audit_log.usuario:
            return f"👤 {obj.audit_log.usuario.get_full_name() or obj.audit_log.usuario.username}"
        return "Sistema"
    usuario_display.short_description = "Usuario"
    
    def accion_display(self, obj):
        acciones_traduccion = {
            'CREATE': 'Crear',
            'UPDATE': 'Actualizar',
            'DELETE': 'Eliminar',
        }
        colores = {
            'CREATE': '#28a745',
            'UPDATE': '#ffc107',
            'DELETE': '#dc3545',
        }
        color = colores.get(obj.audit_log.accion, '#6c757d')
        accion_traducida = acciones_traduccion.get(obj.audit_log.accion, obj.audit_log.get_accion_display())
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, accion_traducida
        )
    accion_display.short_description = "Acción"
    
    def precio_cambio(self, obj):
        if obj.precio_anterior and obj.precio_nuevo:
            return format_html(
                '<span style="color: #d32f2f;">{}</span> → <span style="color: #388e3c;">{}</span>',
                formato_pesos(obj.precio_anterior), formato_pesos(obj.precio_nuevo)
            )
        return "-"
    precio_cambio.short_description = "Precio"
    
    def stock_cambio(self, obj):
        if obj.stock_anterior is not None and obj.stock_nuevo is not None:
            return format_html(
                '<span style="color: #d32f2f;">{}</span> → <span style="color: #388e3c;">{}</span>',
                obj.stock_anterior, obj.stock_nuevo
            )
        return "-"
    stock_cambio.short_description = "Stock"
    
    def descripcion_display(self, obj):
        descripcion = obj.audit_log.descripcion if obj.audit_log.descripcion else "-"
        if len(descripcion) > 60:
            descripcion = descripcion[:60] + "..."
        return descripcion
    descripcion_display.short_description = "Descripción"
    
    def descripcion_completa(self, obj):
        return obj.audit_log.descripcion or "Sin descripción"
    descripcion_completa.short_description = "Descripción Completa"
    
    def precio_display(self, obj):
        return f"Antes: {formato_pesos(obj.precio_anterior)} | Después: {formato_pesos(obj.precio_nuevo)}"
    precio_display.short_description = "Detalles Precio"
    
    def stock_display(self, obj):
        return f"Antes: {obj.stock_anterior} | Después: {obj.stock_nuevo}"
    stock_display.short_description = "Detalles Stock"
    
    def fecha_hora_display(self, obj):
        return obj.audit_log.timestamp.strftime("%d/%m/%Y %H:%M:%S")
    fecha_hora_display.short_description = "Fecha/Hora"
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# ==================== HISTORIAL PEDIDO ====================

class AdminHistorialPedido(admin.ModelAdmin):
    list_display = ('pedido_id_display', 'usuario_display', 'accion_display', 'estado_cambio', 'cliente_display', 'descripcion_display', 'fecha_hora_display')
    list_filter = ('audit_log__accion', 'audit_log__timestamp', 'audit_log__usuario')
    readonly_fields = ('audit_log', 'pedido_id', 'estado_display', 'cliente_display_full', 'descripcion_completa', 'fecha_hora_display')
    
    def pedido_id_display(self, obj):
        """Muestra el ID del pedido en BLANCO"""
        return format_html(
            '<span style="color: #ffffff !important; font-weight: 900;">{}</span>',
            obj.pedido_id
        )
    pedido_id_display.short_description = "Pedido ID"
    
    def usuario_display(self, obj):
        if obj.audit_log.usuario:
            return f"👤 {obj.audit_log.usuario.get_full_name() or obj.audit_log.usuario.username}"
        return "Sistema"
    usuario_display.short_description = "Usuario"
    
    def accion_display(self, obj):
        acciones_traduccion = {
            'CREATE': 'Crear',
            'UPDATE': 'Actualizar',
            'DELETE': 'Eliminar',
        }
        colores = {
            'CREATE': '#28a745',
            'UPDATE': '#ffc107',
            'DELETE': '#dc3545',
        }
        color = colores.get(obj.audit_log.accion, '#6c757d')
        accion_traducida = acciones_traduccion.get(obj.audit_log.accion, obj.audit_log.get_accion_display())
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, accion_traducida
        )
    accion_display.short_description = "Acción"
    
    def estado_cambio(self, obj):
        if obj.estado_anterior and obj.estado_nuevo:
            return format_html(
                '<span style="color: #d32f2f;">❌ {}</span> → <span style="color: #388e3c;">✅ {}</span>',
                obj.estado_anterior, obj.estado_nuevo
            )
        return "-"
    estado_cambio.short_description = "Estado"
    
    def estado_display(self, obj):
        return f"Antes: {obj.estado_anterior} | Después: {obj.estado_nuevo}"
    estado_display.short_description = "Detalles Estado"
    
    def cliente_display(self, obj):
        return obj.cliente_nuevo or "N/A"
    cliente_display.short_description = "Cliente"
    
    def cliente_display_full(self, obj):
        return f"Antes: {obj.cliente_anterior} | Después: {obj.cliente_nuevo}"
    cliente_display_full.short_description = "Detalles Cliente"
    
    def descripcion_display(self, obj):
        descripcion = obj.audit_log.descripcion if obj.audit_log.descripcion else "-"
        if len(descripcion) > 60:
            descripcion = descripcion[:60] + "..."
        return descripcion
    descripcion_display.short_description = "Descripción"
    
    def descripcion_completa(self, obj):
        return obj.audit_log.descripcion or "Sin descripción"
    descripcion_completa.short_description = "Descripción Completa"
    
    def fecha_hora_display(self, obj):
        return obj.audit_log.timestamp.strftime("%d/%m/%Y %H:%M:%S")
    fecha_hora_display.short_description = "Fecha/Hora"
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# ==================== HISTORIAL COTIZACIÓN ====================

class AdminHistorialCotizacion(admin.ModelAdmin):
    list_display = ('cotizacion_id_display', 'usuario_display', 'accion_display', 'estado_cambio', 'monto_cambio', 'descripcion_display', 'fecha_hora_display')
    list_filter = ('audit_log__accion', 'audit_log__timestamp', 'audit_log__usuario')
    readonly_fields = ('audit_log', 'cotizacion_id', 'estado_display', 'monto_display', 'descripcion_completa', 'fecha_hora_display')
    
    def cotizacion_id_display(self, obj):
        """Muestra el ID de la cotización en BLANCO"""
        return format_html(
            '<span style="color: #ffffff !important; font-weight: 900;">{}</span>',
            obj.cotizacion_id
        )
    cotizacion_id_display.short_description = "Cotización ID"
    
    def usuario_display(self, obj):
        if obj.audit_log.usuario:
            return f"👤 {obj.audit_log.usuario.get_full_name() or obj.audit_log.usuario.username}"
        return "Sistema"
    usuario_display.short_description = "Usuario"
    
    def accion_display(self, obj):
        acciones_traduccion = {
            'CREATE': 'Crear',
            'UPDATE': 'Actualizar',
            'DELETE': 'Eliminar',
        }
        colores = {
            'CREATE': '#28a745',
            'UPDATE': '#ffc107',
            'DELETE': '#dc3545',
        }
        color = colores.get(obj.audit_log.accion, '#6c757d')
        accion_traducida = acciones_traduccion.get(obj.audit_log.accion, obj.audit_log.get_accion_display())
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, accion_traducida
        )
    accion_display.short_description = "Acción"
    
    def estado_cambio(self, obj):
        if obj.estado_anterior and obj.estado_nuevo:
            return format_html(
                '<span style="color: #d32f2f;">❌ {}</span> → <span style="color: #388e3c;">✅ {}</span>',
                obj.estado_anterior or "N/A", obj.estado_nuevo or "N/A"
            )
        elif obj.estado_nuevo:
            return format_html(
                '<span style="color: #388e3c;">✅ {}</span>',
                obj.estado_nuevo
            )
        return "N/A"
    estado_cambio.short_description = "Estado"
    
    def monto_cambio(self, obj):
        try:
            monto_anterior = float(obj.monto_anterior) if obj.monto_anterior else None
            monto_nuevo = float(obj.monto_nuevo) if obj.monto_nuevo else None
            
            if monto_anterior and monto_nuevo:
                return format_html(
                    '<span style="color: #d32f2f;">{}</span> → <span style="color: #388e3c;">{}</span>',
                    formato_pesos(monto_anterior), formato_pesos(monto_nuevo)
                )
            elif monto_nuevo:
                return format_html(
                    '<span style="color: #388e3c;">{}</span>',
                    formato_pesos(monto_nuevo)
                )
        except (ValueError, TypeError):
            pass
        return "N/A"
    monto_cambio.short_description = "Monto"
    
    def descripcion_display(self, obj):
        descripcion = obj.audit_log.descripcion if obj.audit_log.descripcion else "-"
        if len(descripcion) > 60:
            descripcion = descripcion[:60] + "..."
        return descripcion
    descripcion_display.short_description = "Descripción"
    
    def descripcion_completa(self, obj):
        return obj.audit_log.descripcion or "Sin descripción"
    descripcion_completa.short_description = "Descripción Completa"
    
    def estado_display(self, obj):
        return f"Antes: {obj.estado_anterior or 'N/A'} | Después: {obj.estado_nuevo or 'N/A'}"
    estado_display.short_description = "Detalles Estado"
    
    def monto_display(self, obj):
        try:
            monto_anterior = float(obj.monto_anterior) if obj.monto_anterior else 0
            monto_nuevo = float(obj.monto_nuevo) if obj.monto_nuevo else 0
            return f"Antes: {formato_pesos(monto_anterior)} | Después: {formato_pesos(monto_nuevo)}"
        except (ValueError, TypeError):
            return "N/A"
    monto_display.short_description = "Detalles Monto"
    
    def fecha_hora_display(self, obj):
        return obj.audit_log.timestamp.strftime("%d/%m/%Y %H:%M:%S")
    fecha_hora_display.short_description = "Fecha/Hora"
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# ==================== HISTORIAL FACTURA ====================

class AdminHistorialFactura(admin.ModelAdmin):
    list_display = ('factura_id_display', 'usuario_display', 'accion_display', 'estado_cambio', 'monto_cambio', 'descripcion_display', 'fecha_hora_display')
    list_filter = ('audit_log__accion', 'audit_log__timestamp', 'audit_log__usuario')
    readonly_fields = ('audit_log', 'factura_id', 'estado_display', 'monto_display', 'descripcion_completa', 'fecha_hora_display')
    
    def factura_id_display(self, obj):
        """Muestra el ID de la factura en BLANCO"""
        return format_html(
            '<span style="color: #ffffff !important; font-weight: 900;">{}</span>',
            obj.factura_id
        )
    factura_id_display.short_description = "Factura ID"
    
    def usuario_display(self, obj):
        if obj.audit_log.usuario:
            return f"👤 {obj.audit_log.usuario.get_full_name() or obj.audit_log.usuario.username}"
        return "Sistema"
    usuario_display.short_description = "Usuario"
    
    def accion_display(self, obj):
        acciones_traduccion = {
            'CREATE': 'Crear',
            'UPDATE': 'Actualizar',
            'DELETE': 'Eliminar',
        }
        colores = {
            'CREATE': '#28a745',
            'UPDATE': '#ffc107',
            'DELETE': '#dc3545',
        }
        color = colores.get(obj.audit_log.accion, '#6c757d')
        accion_traducida = acciones_traduccion.get(obj.audit_log.accion, obj.audit_log.get_accion_display())
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, accion_traducida
        )
    accion_display.short_description = "Acción"
    
    def estado_cambio(self, obj):
        if obj.estado_anterior and obj.estado_nuevo:
            return format_html(
                '<span style="color: #d32f2f;">❌ {}</span> → <span style="color: #388e3c;">✅ {}</span>',
                obj.estado_anterior or "N/A", obj.estado_nuevo or "N/A"
            )
        elif obj.estado_nuevo:
            return format_html(
                '<span style="color: #388e3c;">✅ {}</span>',
                obj.estado_nuevo
            )
        return "N/A"
    estado_cambio.short_description = "Estado"
    
    def monto_cambio(self, obj):
        try:
            monto_anterior = float(obj.monto_anterior) if obj.monto_anterior else None
            monto_nuevo = float(obj.monto_nuevo) if obj.monto_nuevo else None
            
            if monto_anterior and monto_nuevo:
                return format_html(
                    '<span style="color: #d32f2f;">{}</span> → <span style="color: #388e3c;">{}</span>',
                    formato_pesos(monto_anterior), formato_pesos(monto_nuevo)
                )
            elif monto_nuevo:
                return format_html(
                    '<span style="color: #388e3c;">{}</span>',
                    formato_pesos(monto_nuevo)
                )
        except (ValueError, TypeError):
            pass
        return "N/A"
    monto_cambio.short_description = "Monto"
    
    def descripcion_display(self, obj):
        descripcion = obj.audit_log.descripcion if obj.audit_log.descripcion else "-"
        if len(descripcion) > 60:
            descripcion = descripcion[:60] + "..."
        return descripcion
    descripcion_display.short_description = "Descripción"
    
    def descripcion_completa(self, obj):
        return obj.audit_log.descripcion or "Sin descripción"
    descripcion_completa.short_description = "Descripción Completa"
    
    def estado_display(self, obj):
        return f"Antes: {obj.estado_anterior or 'N/A'} | Después: {obj.estado_nuevo or 'N/A'}"
    estado_display.short_description = "Detalles Estado"
    
    def monto_display(self, obj):
        try:
            monto_anterior = float(obj.monto_anterior) if obj.monto_anterior else 0
            monto_nuevo = float(obj.monto_nuevo) if obj.monto_nuevo else 0
            return f"Antes: {formato_pesos(monto_anterior)} | Después: {formato_pesos(monto_nuevo)}"
        except (ValueError, TypeError):
            return "N/A"
    monto_display.short_description = "Detalles Monto"
    
    def fecha_hora_display(self, obj):
        return obj.audit_log.timestamp.strftime("%d/%m/%Y %H:%M:%S")
    fecha_hora_display.short_description = "Fecha/Hora"
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# ==================== HISTORIAL CLIENTE ====================

class AdminHistorialCliente(admin.ModelAdmin):
    list_display = ('cliente_id_display', 'usuario_display', 'accion_display', 'cambios_preview', 'descripcion_display', 'fecha_hora_display')
    list_filter = ('audit_log__accion', 'audit_log__timestamp', 'audit_log__usuario')
    readonly_fields = ('audit_log', 'cliente_id', 'cambios_display', 'descripcion_completa', 'fecha_hora_display')
    
    def cliente_id_display(self, obj):
        """Muestra el ID del cliente en BLANCO"""
        return format_html(
            '<span style="color: #ffffff !important; font-weight: 900;">{}</span>',
            obj.cliente_id
        )
    cliente_id_display.short_description = "Cliente ID"
    
    def usuario_display(self, obj):
        if obj.audit_log.usuario:
            return f"👤 {obj.audit_log.usuario.get_full_name() or obj.audit_log.usuario.username}"
        return "Sistema"
    usuario_display.short_description = "Usuario"
    
    def accion_display(self, obj):
        acciones_traduccion = {
            'CREATE': 'Crear',
            'UPDATE': 'Actualizar',
            'DELETE': 'Eliminar',
        }
        colores = {
            'CREATE': '#28a745',
            'UPDATE': '#ffc107',
            'DELETE': '#dc3545',
        }
        color = colores.get(obj.audit_log.accion, '#6c757d')
        accion_traducida = acciones_traduccion.get(obj.audit_log.accion, obj.audit_log.get_accion_display())
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, accion_traducida
        )
    accion_display.short_description = "Acción"
    
    def cambios_preview(self, obj):
        if obj.cambios:
            campos = ', '.join(obj.cambios.keys())
            return f"Cambios en: {campos}"
        return "-"
    cambios_preview.short_description = "Cambios"
    
    def cambios_display(self, obj):
        import json
        if not obj.cambios:
            return "Sin cambios"
        datos = json.dumps(obj.cambios, indent=2, ensure_ascii=False)
        return format_html('<pre style="background: #f4f4f4; padding: 10px;">{}</pre>', datos)
    cambios_display.short_description = "Detalles Cambios"
    
    def descripcion_display(self, obj):
        descripcion = obj.audit_log.descripcion if obj.audit_log.descripcion else "-"
        if len(descripcion) > 60:
            descripcion = descripcion[:60] + "..."
        return descripcion
    descripcion_display.short_description = "Descripción"
    
    def descripcion_completa(self, obj):
        return obj.audit_log.descripcion or "Sin descripción"
    descripcion_completa.short_description = "Descripción Completa"
    
    def fecha_hora_display(self, obj):
        return obj.audit_log.timestamp.strftime("%d/%m/%Y %H:%M:%S")
    fecha_hora_display.short_description = "Fecha/Hora"
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# ==================== HISTORIAL CATEGORÍA ====================

class AdminHistorialCategoria(admin.ModelAdmin):
    list_display = ('categoria_id_display', 'usuario_display', 'accion_display', 'nombre_cambio', 'descripcion_display', 'fecha_hora_display')
    list_filter = ('audit_log__accion', 'audit_log__timestamp', 'audit_log__usuario')
    readonly_fields = ('audit_log', 'categoria_id', 'nombre_display', 'descripcion_detail', 'descripcion_completa', 'fecha_hora_display')
    
    def categoria_id_display(self, obj):
        """Muestra el ID de la categoría en BLANCO"""
        return format_html(
            '<span style="color: #ffffff !important; font-weight: 900;">{}</span>',
            obj.categoria_id
        )
    categoria_id_display.short_description = "Categoría ID"
    
    def usuario_display(self, obj):
        if obj.audit_log.usuario:
            return f"👤 {obj.audit_log.usuario.get_full_name() or obj.audit_log.usuario.username}"
        return "Sistema"
    usuario_display.short_description = "Usuario"
    
    def accion_display(self, obj):
        acciones_traduccion = {
            'CREATE': 'Crear',
            'UPDATE': 'Actualizar',
            'DELETE': 'Eliminar',
        }
        colores = {
            'CREATE': '#28a745',
            'UPDATE': '#ffc107',
            'DELETE': '#dc3545',
        }
        color = colores.get(obj.audit_log.accion, '#6c757d')
        accion_traducida = acciones_traduccion.get(obj.audit_log.accion, obj.audit_log.get_accion_display())
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, accion_traducida
        )
    accion_display.short_description = "Acción"
    
    def nombre_cambio(self, obj):
        if obj.nombre_anterior and obj.nombre_nuevo:
            return format_html(
                '<span style="color: #d32f2f;">{}</span> → <span style="color: #388e3c;">{}</span>',
                obj.nombre_anterior, obj.nombre_nuevo
            )
        return obj.nombre_nuevo or "-"
    nombre_cambio.short_description = "Nombre"
    
    def nombre_display(self, obj):
        return f"Antes: {obj.nombre_anterior} | Después: {obj.nombre_nuevo}"
    nombre_display.short_description = "Detalles Nombre"
    
    def descripcion_detail(self, obj):
        return f"Antes: {obj.descripcion_anterior} | Después: {obj.descripcion_nueva}"
    descripcion_detail.short_description = "Detalles Descripción"
    
    def descripcion_display(self, obj):
        descripcion = obj.audit_log.descripcion if obj.audit_log.descripcion else "-"
        if len(descripcion) > 60:
            descripcion = descripcion[:60] + "..."
        return descripcion
    descripcion_display.short_description = "Descripción"
    
    def descripcion_completa(self, obj):
        return obj.audit_log.descripcion or "Sin descripción"
    descripcion_completa.short_description = "Descripción Completa"
    
    def fecha_hora_display(self, obj):
        return obj.audit_log.timestamp.strftime("%d/%m/%Y %H:%M:%S")
    fecha_hora_display.short_description = "Fecha/Hora"
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# ==================== REGISTRAR MODELOS ====================

admin.site.register(AuditLog, AdminRegistroAuditoria)
admin.site.register(HistorialProducto, AdminHistorialProducto)
admin.site.register(HistorialPedido, AdminHistorialPedido)
admin.site.register(HistorialCotizacion, AdminHistorialCotizacion)
admin.site.register(HistorialFactura, AdminHistorialFactura)
admin.site.register(HistorialCliente, AdminHistorialCliente)
admin.site.register(HistorialCategoria, AdminHistorialCategoria)