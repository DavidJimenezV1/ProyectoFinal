from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from inventario.models import Producto, Categoria
from pedidos.models import Pedido, Cliente
from cotizaciones.models import Cotizacion
from ventas.models import Factura
from auditorias.models import (
    AuditLog,
    HistorialProducto,
    HistorialPedido,
    HistorialCotizacion,
    HistorialFactura,
    HistorialCliente,
    HistorialCategoria
)

User = get_user_model()


class AuditLogModelTest(TestCase):
    """Tests para el modelo AuditLog"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.categoria = Categoria.objects.create(
            nombre='Test Categoria',
            descripcion='Descripción de prueba'
        )
        
        self.producto = Producto.objects.create(
            nombre='Test Producto',
            codigo='TEST001',
            descripcion='Descripción del producto',
            precio=100.00,
            stock=10,
            categoria=self.categoria
        )
    
    def test_audit_log_creation(self):
        """Test para crear un registro de auditoría"""
        content_type = ContentType.objects.get_for_model(Producto)
        
        audit_log = AuditLog.objects.create(
            usuario=self.user,
            usuario_nombre=self.user.get_full_name(),
            accion=AuditLog.ACTION_CREATE,
            content_type=content_type,
            object_id=self.producto.id,
            modelo='Producto',
            objeto_repr=str(self.producto),
            cambios={}
        )
        
        self.assertIsNotNone(audit_log.id)
        self.assertEqual(audit_log.usuario, self.user)
        self.assertEqual(audit_log.accion, AuditLog.ACTION_CREATE)
        self.assertEqual(audit_log.modelo, 'Producto')
    
    def test_audit_log_str(self):
        """Test para el método __str__ de AuditLog"""
        content_type = ContentType.objects.get_for_model(Producto)
        
        audit_log = AuditLog.objects.create(
            usuario=self.user,
            usuario_nombre='Test User',
            accion=AuditLog.ACTION_UPDATE,
            content_type=content_type,
            object_id=self.producto.id,
            modelo='Producto',
            objeto_repr=str(self.producto),
            cambios={'precio': {'anterior': '100.00', 'nuevo': '150.00'}}
        )
        
        self.assertIn('UPDATE', str(audit_log))
        self.assertIn('Producto', str(audit_log))
        self.assertIn('Test User', str(audit_log))
    
    def test_cambios_formateados(self):
        """Test para el método cambios_formateados"""
        content_type = ContentType.objects.get_for_model(Producto)
        
        cambios = {
            'precio': {'anterior': '100.00', 'nuevo': '150.00'},
            'stock': {'anterior': '10', 'nuevo': '20'}
        }
        
        audit_log = AuditLog.objects.create(
            usuario=self.user,
            usuario_nombre='Test User',
            accion=AuditLog.ACTION_UPDATE,
            content_type=content_type,
            object_id=self.producto.id,
            modelo='Producto',
            objeto_repr=str(self.producto),
            cambios=cambios
        )
        
        formatted = audit_log.cambios_formateados
        self.assertIn('precio', formatted)
        self.assertIn('stock', formatted)


class HistorialProductoTest(TestCase):
    """Tests para el modelo HistorialProducto"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.categoria = Categoria.objects.create(nombre='Test Categoria')
        
        self.producto = Producto.objects.create(
            nombre='Test Producto',
            codigo='TEST001',
            descripcion='Descripción',
            precio=100.00,
            stock=10,
            categoria=self.categoria
        )
    
    def test_historial_producto_creation(self):
        """Test para crear historial de producto"""
        historial = HistorialProducto.objects.create(
            producto=self.producto,
            usuario=self.user,
            precio_anterior=100.00,
            precio_nuevo=150.00,
            stock_anterior=10,
            stock_nuevo=20,
            descripcion='Actualización de precio y stock'
        )
        
        self.assertIsNotNone(historial.id)
        self.assertEqual(historial.producto, self.producto)
        self.assertEqual(historial.precio_nuevo, 150.00)
        self.assertEqual(historial.stock_nuevo, 20)
    
    def test_historial_producto_str(self):
        """Test para el método __str__"""
        historial = HistorialProducto.objects.create(
            producto=self.producto,
            usuario=self.user,
            descripcion='Test'
        )
        
        self.assertIn(str(self.producto), str(historial))


class HistorialPedidoTest(TestCase):
    """Tests para el modelo HistorialPedido"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.cliente = Cliente.objects.create(
            nombre='Cliente',
            apellido='Test',
            email='cliente@test.com',
            telefono='123456789',
            direccion='Calle Test'
        )
        
        self.pedido = Pedido.objects.create(
            cliente=self.cliente,
            estado='pendiente'
        )
    
    def test_historial_pedido_creation(self):
        """Test para crear historial de pedido"""
        historial = HistorialPedido.objects.create(
            pedido=self.pedido,
            usuario=self.user,
            estado_anterior='pendiente',
            estado_nuevo='en_proceso',
            descripcion='Cambio de estado a en proceso'
        )
        
        self.assertIsNotNone(historial.id)
        self.assertEqual(historial.pedido, self.pedido)
        self.assertEqual(historial.estado_nuevo, 'en_proceso')


class AuditLogAdminTest(TestCase):
    """Tests para el admin de auditoría"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@test.com'
        )
        
        self.categoria = Categoria.objects.create(nombre='Test')
        self.producto = Producto.objects.create(
            nombre='Test',
            codigo='TEST001',
            descripcion='Test',
            precio=100,
            stock=10,
            categoria=self.categoria
        )
    
    def test_audit_log_admin_permissions(self):
        """Test de permisos del admin de auditoría"""
        from auditorias.admin import AuditLogAdmin
        from django.contrib.admin.sites import AdminSite
        
        site = AdminSite()
        admin = AuditLogAdmin(AuditLog, site)
        
        # Test que no se puede agregar registros manualmente
        self.assertFalse(admin.has_add_permission(None))
        
        # Test que solo superusuarios pueden eliminar
        self.assertTrue(admin.has_delete_permission(MockRequest(self.user)))
    
    def test_audit_log_queryset_filtering(self):
        """Test del filtrado de queryset por usuario"""
        from auditorias.admin import AuditLogAdmin
        from django.contrib.admin.sites import AdminSite
        
        site = AdminSite()
        admin = AuditLogAdmin(AuditLog, site)
        
        # Crear usuario normal
        normal_user = User.objects.create_user(
            username='normal',
            password='pass123'
        )
        
        # Superusuario debe ver todos los registros
        request = MockRequest(self.user)
        qs = admin.get_queryset(request)
        self.assertEqual(qs.model, AuditLog)


class MockRequest:
    """Mock request para tests"""
    def __init__(self, user):
        self.user = user
