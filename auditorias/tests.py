from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from inventario.models import Producto, Categoria
from pedidos.models import Pedido, Cliente
from auditorias.models import Auditoria

User = get_user_model()


class AuditoriaSignalsTest(TestCase):
    """Tests para verificar que los signals de auditoría funcionan correctamente"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        # Crear un usuario de prueba
        self.usuario = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Crear una categoría de prueba
        self.categoria = Categoria.objects.create(
            nombre='Categoría Test',
            descripcion='Descripción de prueba'
        )
    
    def test_auditoria_creacion_producto(self):
        """Verifica que se registre la creación de un producto"""
        # Contar auditorías antes
        auditorias_antes = Auditoria.objects.count()
        
        # Crear un producto
        producto = Producto.objects.create(
            nombre='Producto Test',
            codigo='TEST001',
            descripcion='Descripción de test',
            precio=100.00,
            stock=10,
            categoria=self.categoria
        )
        
        # Verificar que se creó una auditoría
        auditorias_despues = Auditoria.objects.count()
        self.assertEqual(auditorias_despues, auditorias_antes + 1)
        
        # Verificar detalles de la auditoría
        auditoria = Auditoria.objects.latest('fecha_hora')
        self.assertEqual(auditoria.accion, 'CREATE')
        self.assertEqual(auditoria.object_id, producto.id)
        self.assertEqual(
            auditoria.content_type,
            ContentType.objects.get_for_model(Producto)
        )
    
    def test_auditoria_actualizacion_producto(self):
        """Verifica que se registre la actualización de un producto"""
        # Crear un producto
        producto = Producto.objects.create(
            nombre='Producto Test',
            codigo='TEST001',
            descripcion='Descripción de test',
            precio=100.00,
            stock=10,
            categoria=self.categoria
        )
        
        # Contar auditorías antes de la actualización
        auditorias_antes = Auditoria.objects.filter(accion='UPDATE').count()
        
        # Actualizar el producto
        producto.precio = 150.00
        producto.stock = 15
        producto.save()
        
        # Verificar que se creó una auditoría de actualización
        auditorias_despues = Auditoria.objects.filter(accion='UPDATE').count()
        self.assertEqual(auditorias_despues, auditorias_antes + 1)
        
        # Verificar detalles de la auditoría
        auditoria = Auditoria.objects.filter(accion='UPDATE').latest('fecha_hora')
        self.assertEqual(auditoria.object_id, producto.id)
        self.assertIsNotNone(auditoria.cambios)
    
    def test_auditoria_eliminacion_producto(self):
        """Verifica que se registre la eliminación de un producto"""
        # Crear un producto
        producto = Producto.objects.create(
            nombre='Producto Test',
            codigo='TEST001',
            descripcion='Descripción de test',
            precio=100.00,
            stock=10,
            categoria=self.categoria
        )
        producto_id = producto.id
        
        # Contar auditorías antes de la eliminación
        auditorias_antes = Auditoria.objects.filter(accion='DELETE').count()
        
        # Eliminar el producto
        producto.delete()
        
        # Verificar que se creó una auditoría de eliminación
        auditorias_despues = Auditoria.objects.filter(accion='DELETE').count()
        self.assertEqual(auditorias_despues, auditorias_antes + 1)
        
        # Verificar detalles de la auditoría
        auditoria = Auditoria.objects.filter(accion='DELETE').latest('fecha_hora')
        self.assertEqual(auditoria.object_id, producto_id)
    
    def test_auditoria_categoria(self):
        """Verifica que se auditen las categorías"""
        auditorias_antes = Auditoria.objects.count()
        
        # Crear una nueva categoría
        categoria = Categoria.objects.create(
            nombre='Nueva Categoría',
            descripcion='Nueva descripción'
        )
        
        # Verificar que se creó una auditoría
        auditorias_despues = Auditoria.objects.count()
        self.assertGreater(auditorias_despues, auditorias_antes)
    
    def test_auditoria_cliente(self):
        """Verifica que se auditen los clientes"""
        auditorias_antes = Auditoria.objects.count()
        
        # Crear un cliente
        cliente = Cliente.objects.create(
            nombre='Juan',
            apellido='Pérez',
            email='juan@example.com',
            telefono='123456789',
            direccion='Calle Test 123'
        )
        
        # Verificar que se creó una auditoría
        auditorias_despues = Auditoria.objects.count()
        self.assertGreater(auditorias_despues, auditorias_antes)
        
        # Verificar el tipo de contenido
        auditoria = Auditoria.objects.latest('fecha_hora')
        self.assertEqual(
            auditoria.content_type,
            ContentType.objects.get_for_model(Cliente)
        )
    
    def test_cambios_formateados(self):
        """Verifica que el método cambios_formateados funcione correctamente"""
        # Crear y actualizar un producto para generar cambios
        producto = Producto.objects.create(
            nombre='Producto Test',
            codigo='TEST001',
            descripcion='Descripción de test',
            precio=100.00,
            stock=10,
            categoria=self.categoria
        )
        
        producto.precio = 150.00
        producto.save()
        
        # Obtener la auditoría de actualización
        auditoria = Auditoria.objects.filter(
            accion='UPDATE',
            object_id=producto.id
        ).latest('fecha_hora')
        
        # Verificar que cambios_formateados devuelve algo
        cambios_texto = auditoria.cambios_formateados()
        self.assertIsNotNone(cambios_texto)
        self.assertIsInstance(cambios_texto, str)
