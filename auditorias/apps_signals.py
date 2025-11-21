"""
Módulo para conectar automáticamente los signals de auditoría a todos los modelos relevantes.
Este archivo es importado por apps.py cuando la aplicación está lista.
"""
from django.apps import apps
from .signals import conectar_signals_modelo


def conectar_signals_todas_apps():
    """
    Conecta los signals de auditoría a todos los modelos especificados.
    """
    # Lista de modelos a auditar: (app_label, model_name)
    modelos_a_auditar = [
        # Productos y Categorías
        ('inventario', 'Producto'),
        ('inventario', 'Categoria'),
        ('inventario', 'ImagenProducto'),
        
        # Pedidos y Clientes
        ('pedidos', 'Pedido'),
        ('pedidos', 'Cliente'),
        ('pedidos', 'DetallePedido'),
        
        # Cotizaciones
        ('cotizaciones', 'Cotizacion'),
        ('cotizaciones', 'DetalleCotizacion'),
        
        # Facturas
        ('ventas', 'Factura'),
        ('ventas', 'ItemFactura'),
    ]
    
    # Conectar signals para cada modelo
    for app_label, model_name in modelos_a_auditar:
        try:
            modelo = apps.get_model(app_label, model_name)
            conectar_signals_modelo(modelo)
            print(f"✓ Signals de auditoría conectados para {app_label}.{model_name}")
        except LookupError:
            print(f"✗ Advertencia: No se pudo encontrar el modelo {app_label}.{model_name}")
        except Exception as e:
            print(f"✗ Error al conectar signals para {app_label}.{model_name}: {e}")


# Ejecutar la conexión de signals al importar este módulo
conectar_signals_todas_apps()
