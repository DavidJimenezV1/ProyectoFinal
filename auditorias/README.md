# Sistema de Auditorías

## Descripción

Este módulo proporciona un sistema completo de auditoría automática para rastrear todas las operaciones de Crear, Actualizar y Eliminar (CRUD) en los modelos críticos del sistema.

## Modelos Auditados

El sistema audita automáticamente los siguientes modelos:

### Inventario
- **Producto**: Cambios en productos (precio, stock, nombre, etc.)
- **Categoría**: Cambios en categorías
- **ImagenProducto**: Cambios en imágenes de productos

### Pedidos
- **Pedido**: Cambios en pedidos
- **Cliente**: Cambios en información de clientes
- **DetallePedido**: Cambios en detalles de pedidos

### Cotizaciones
- **Cotización**: Cambios en cotizaciones
- **DetalleCotización**: Cambios en detalles de cotizaciones

### Ventas
- **Factura**: Cambios en facturas
- **ItemFactura**: Cambios en items de facturas

## Características

### 1. Registro Automático
Todas las operaciones se registran automáticamente mediante Django signals, sin necesidad de código adicional en los modelos.

### 2. Información Capturada
- **Usuario**: Usuario que realizó la acción (si está disponible)
- **Acción**: Tipo de operación (CREATE, UPDATE, DELETE)
- **Fecha y Hora**: Timestamp preciso de la operación
- **Dirección IP**: IP desde donde se realizó la operación (si está disponible)
- **Cambios**: Valores anteriores y nuevos para actualizaciones
- **Objeto**: Representación del objeto afectado

### 3. Interfaz de Administración
El modelo de Auditoría está disponible en el panel de administración de Django con:
- **Filtros personalizados**:
  - Por período de tiempo (hoy, ayer, última semana, último mes, último trimestre)
  - Por tipo de acción (crear, actualizar, eliminar)
  - Por tipo de modelo
  - Por usuario
- **Búsqueda**: Por representación del objeto, nombre de usuario, email o IP
- **Solo lectura**: Las auditorías no pueden ser editadas ni eliminadas desde el admin

### 4. Vistas Personalizadas
- **Dashboard**: Vista general con estadísticas y registros recientes
- **Detalle**: Vista detallada de una auditoría específica
- **Historial**: Historial completo de cambios de un objeto

## Uso

### Acceder a las Auditorías

#### Desde el Admin de Django
1. Ir a `/admin/`
2. Buscar la sección "Sistema de Auditorías"
3. Click en "Auditorías"

#### Desde las Vistas Personalizadas
- Dashboard: `/auditorias/`
- Detalle: `/auditorias/detalle/<id>/`
- Historial: `/auditorias/historial/<content_type_id>/<object_id>/`

### Consultar Auditorías Programáticamente

```python
from auditorias.models import Auditoria
from django.contrib.contenttypes.models import ContentType

# Obtener todas las auditorías de un modelo
from inventario.models import Producto
ct = ContentType.objects.get_for_model(Producto)
auditorias = Auditoria.objects.filter(content_type=ct)

# Obtener auditorías de un objeto específico
producto_id = 1
auditorias_producto = Auditoria.objects.filter(
    content_type=ct,
    object_id=producto_id
)

# Obtener auditorías de un usuario
from usuarios.models import Usuario
user = Usuario.objects.get(username='admin')
auditorias_usuario = Auditoria.objects.filter(usuario=user)

# Obtener auditorías por tipo de acción
creaciones = Auditoria.objects.filter(accion='CREATE')
actualizaciones = Auditoria.objects.filter(accion='UPDATE')
eliminaciones = Auditoria.objects.filter(accion='DELETE')
```

### Formatear Cambios

```python
auditoria = Auditoria.objects.first()
cambios_legibles = auditoria.cambios_formateados()
print(cambios_legibles)
# Output: "precio: '100.00' → '150.00'\nstock: '10' → '20'"
```

## Configuración

### Agregar Nuevos Modelos a Auditar

Para auditar un modelo adicional, editar `auditorias/apps_signals.py`:

```python
modelos_a_auditar = [
    # ... modelos existentes ...
    ('nombre_app', 'NombreModelo'),
]
```

### Excluir Campos de la Auditoría

En `auditorias/signals.py`, función `obtener_cambios()`:

```python
campos_excluir = [
    'fecha_actualizacion', 
    'fecha_creacion',
    'campo_a_excluir'  # Agregar aquí
]
```

## Consideraciones de Rendimiento

El sistema realiza una consulta adicional a la base de datos por cada operación de actualización para obtener el estado anterior del objeto. Para sistemas con alta carga:

1. Las consultas están optimizadas usando `only()` para cargar solo los campos necesarios
2. Considerar implementar un sistema de caché para estados anteriores
3. Usar `select_related()` y `prefetch_related()` en operaciones que disparen múltiples actualizaciones

## Seguridad

- Las auditorías son de **solo lectura** desde el admin
- No se pueden crear, editar o eliminar auditorías manualmente
- Solo usuarios staff pueden acceder a las vistas de auditoría
- Los cambios incluyen información sensible - proteger el acceso apropiadamente

## Tests

Para ejecutar los tests del sistema de auditorías:

```bash
python manage.py test auditorias
```

Los tests verifican:
- Registro de creaciones
- Registro de actualizaciones con cambios
- Registro de eliminaciones
- Funcionamiento de filtros
- Formato de cambios
- Auditoría de todos los modelos configurados
