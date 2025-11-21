# Sistema de Auditoría - Tejos Olímpica

## Descripción General

El sistema de auditoría proporciona un registro completo y automático de todas las acciones realizadas en el sistema, incluyendo creación, actualización y eliminación de registros. Está diseñado para ser modular, extensible y cumplir con los requisitos de trazabilidad empresarial.

## Características Principales

### 1. Auditoría General (AuditLog)

El modelo `AuditLog` registra automáticamente todas las operaciones en los modelos principales:

- **Acciones capturadas**: CREATE, UPDATE, DELETE
- **Información registrada**:
  - Usuario que realizó la acción
  - Fecha y hora exacta
  - Tipo de modelo afectado
  - ID del objeto modificado
  - Cambios específicos (valores anteriores y nuevos)
  - Dirección IP y User Agent
  - Notas adicionales

### 2. Historiales Específicos

Se implementaron modelos de historial específicos para cada entidad principal:

#### HistorialProducto
- Seguimiento de cambios en nombre, precio y stock
- Alertas de cambios significativos
- Registro de ajustes de inventario

#### HistorialPedido
- Registro de cambios de estado
- Seguimiento del flujo del pedido
- Historial de modificaciones

#### HistorialCotizacion
- Cambios de estado y montos
- Seguimiento de aprobaciones/rechazos
- Registro de revisiones

#### HistorialFactura
- Seguimiento de pagos
- Cambios en totales
- Estados de facturación

#### HistorialCliente
- Cambios en datos del cliente
- Actualización de información de contacto

#### HistorialCategoria
- Cambios en categorías de productos
- Reorganización del catálogo

## Cómo Funciona

### Sistema de Signals

El sistema utiliza Django signals para capturar automáticamente los cambios:

```python
# Signals automáticos
@receiver(pre_save)  # Guarda el estado anterior
@receiver(post_save)  # Registra creación/actualización
@receiver(post_delete)  # Registra eliminación
```

### Middleware de Usuario

El middleware `CurrentUserMiddleware` captura el usuario actual en cada solicitud:

```python
# En settings.py
MIDDLEWARE = [
    ...
    'auditorias.middleware.CurrentUserMiddleware',
]
```

## Panel de Administración

### Filtros Avanzados

El admin de auditoría incluye filtros por:

- **Rango de fecha**:
  - Hoy
  - Ayer
  - Última semana
  - Último mes
  - Último trimestre
  - Último año

- **Tipo de acción**: CREATE, UPDATE, DELETE
- **Modelo afectado**: Producto, Pedido, Cotización, etc.
- **Usuario**: Filtrar por usuario específico

### Búsqueda Avanzada

Buscar por:
- Nombre de usuario
- Nombre del modelo
- Representación del objeto
- Notas adicionales

### Exportación de Datos

- **CSV**: Exportar registros seleccionados a CSV
- **Excel**: Compatible con Excel para análisis

### Visualización

- **Badges con colores**: Estados visuales claros
- **Formato de cambios**: JSON legible de cambios realizados
- **Información temporal**: Fecha y hora formateadas
- **Identificación de usuario**: Badges de usuario/sistema

## Permisos y Seguridad

### Niveles de Acceso

1. **Superusuarios (Admin Mayor)**:
   - Acceso completo a todos los registros
   - Puede eliminar registros de auditoría
   - Ve estadísticas globales

2. **Administradores**:
   - Ven todos los registros del sistema
   - No pueden eliminar auditorías
   - Acceso de solo lectura

3. **Usuarios Normales**:
   - Solo ven sus propias acciones
   - Acceso restringido por filtros automáticos

### Protecciones

- **No editable**: Los registros de auditoría no se pueden editar
- **No creación manual**: No se pueden crear registros manualmente
- **Solo lectura**: La mayoría de campos son de solo lectura
- **Eliminación restringida**: Solo superusuarios pueden eliminar

## Mejoras en AdminClasses Existentes

### ProductoAdmin

**Nuevas características**:
- Estado de stock con indicadores visuales (✅ ❌ ⚠️)
- Búsqueda avanzada con autocomplete
- Exportación a CSV
- Acciones en lote:
  - Identificar productos con bajo stock
  - Exportar selección a CSV
- Filtros por categoría y fecha
- Vista previa de imágenes

### PedidoAdmin

**Mejoras implementadas**:
- Badges de estado con colores
- Visualización del total calculado
- Búsqueda por cliente
- Acciones en lote:
  - Cambiar a "En Proceso"
  - Marcar como "Completado"
  - Marcar como "Cancelado"
- Exportación a CSV
- Autocomplete en cliente y productos

### CotizacionAdmin

**Características añadidas**:
- Visualización de totales con/sin IVA
- Badges de estado
- Contador de items
- Acciones rápidas:
  - Marcar como Revisada
  - Marcar como Aprobada
  - Marcar como Rechazada
- Exportación a CSV
- Botones de descarga PDF

### FacturaAdmin

**Mejoras**:
- Badges de estado con colores
- Indicador de IVA incluido
- Cálculo automático de totales
- Acciones en lote:
  - Marcar como Pagada
  - Marcar como Cancelada
- Exportación a CSV
- Descarga de PDF
- Autocomplete en productos

### ClienteAdmin

**Nuevas funcionalidades**:
- Contador de pedidos por cliente
- Fecha del último pedido
- Exportación a CSV
- Búsqueda mejorada

### CategoriaAdmin

**Mejoras**:
- Contador de productos por categoría
- Vista mejorada con badges

## Uso en Código

### Consultar el Historial de un Objeto

```python
# Obtener historial de un producto
producto = Producto.objects.get(id=1)
historial = producto.historial.all().order_by('-fecha_hora')

# Iterar sobre el historial
for registro in historial:
    print(f"{registro.fecha_hora}: {registro.descripcion}")
```

### Crear un Registro Manual (si es necesario)

```python
from auditorias.models import AuditLog
from django.contrib.contenttypes.models import ContentType

# Crear registro manual
content_type = ContentType.objects.get_for_model(MiModelo)
AuditLog.objects.create(
    usuario=request.user,
    usuario_nombre=request.user.get_full_name(),
    accion=AuditLog.ACTION_UPDATE,
    content_type=content_type,
    object_id=objeto.id,
    modelo='MiModelo',
    objeto_repr=str(objeto),
    cambios={'campo': {'anterior': 'valor1', 'nuevo': 'valor2'}}
)
```

### Filtrar Auditorías

```python
from auditorias.models import AuditLog
from datetime import datetime, timedelta

# Auditorías de las últimas 24 horas
hace_24h = datetime.now() - timedelta(days=1)
recientes = AuditLog.objects.filter(fecha_hora__gte=hace_24h)

# Auditorías de un usuario específico
mis_acciones = AuditLog.objects.filter(usuario=request.user)

# Auditorías de un modelo específico
productos_modificados = AuditLog.objects.filter(modelo='Producto')
```

## Configuración

### Modelos a Auditar

Por defecto, se auditan los modelos de las apps:
- `inventario`
- `pedidos`
- `cotizaciones`
- `ventas`
- `usuarios`

Para agregar más apps, editar en `auditorias/signals.py`:

```python
# En las funciones de signal
if sender._meta.app_label not in ['inventario', 'pedidos', 'tu_nueva_app']:
    return
```

### Desactivar Auditoría Temporalmente

Si necesitas hacer operaciones masivas sin auditoría:

```python
from django.db.models.signals import post_save, post_delete
from auditorias.signals import create_audit_log, create_delete_audit_log

# Desconectar signals
post_save.disconnect(create_audit_log)
post_delete.disconnect(create_delete_audit_log)

# Hacer operaciones
# ...

# Reconectar signals
post_save.connect(create_audit_log)
post_delete.connect(create_delete_audit_log)
```

## Mantenimiento

### Limpieza de Registros Antiguos

Se recomienda establecer una política de retención:

```python
# Script de mantenimiento (management command recomendado)
from datetime import datetime, timedelta
from auditorias.models import AuditLog

# Eliminar auditorías de más de 2 años
fecha_limite = datetime.now() - timedelta(days=730)
AuditLog.objects.filter(fecha_hora__lt=fecha_limite).delete()
```

### Monitoreo de Espacio

Las auditorías pueden crecer rápidamente. Monitorear:
- Tamaño de la tabla `auditorias_auditlog`
- Cantidad de registros
- Rendimiento de consultas

## Troubleshooting

### El usuario aparece como "Sistema"

**Causa**: El middleware no está capturando el usuario o la acción se ejecuta fuera de una solicitud HTTP.

**Solución**: Verificar que `CurrentUserMiddleware` esté en `MIDDLEWARE` en settings.py.

### No se registran cambios

**Causa**: Los signals no están conectados o la app no está en la lista de apps auditadas.

**Solución**: 
1. Verificar que `auditorias` esté en `INSTALLED_APPS`
2. Verificar que `ready()` en `AuditoriasConfig` importe los signals
3. Verificar que el modelo esté en una app auditada

### Errores de rendimiento

**Causa**: Demasiados registros de auditoría.

**Solución**:
1. Implementar política de limpieza
2. Indexar campos de búsqueda frecuente
3. Usar paginación en consultas

## Próximas Mejoras

- [ ] Dashboard de estadísticas de auditoría
- [ ] Gráficos de actividad por usuario/modelo
- [ ] Alertas automáticas para acciones críticas
- [ ] Integración con sistema de notificaciones
- [ ] Exportación a más formatos (JSON, XML)
- [ ] API REST para consultas de auditoría
- [ ] Comparación visual de cambios (diff)
- [ ] Reversión de cambios (rollback)

## Soporte

Para preguntas o problemas con el sistema de auditoría, contactar al equipo de desarrollo.
