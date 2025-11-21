"""
Management command para generar datos de demostración del sistema de auditoría.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from inventario.models import Producto, Categoria
from pedidos.models import Pedido, Cliente
from auditorias.models import AuditLog
from threading import current_thread
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Genera datos de demostración para el sistema de auditoría'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Limpiar datos de auditoría existentes antes de generar nuevos',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Generador de Datos de Auditoría ===\n'))

        # Limpiar si se solicita
        if options['clean']:
            self.stdout.write('Limpiando datos de auditoría existentes...')
            AuditLog.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Datos limpiados\n'))

        # Obtener o crear usuario
        user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={
                'first_name': 'Usuario',
                'last_name': 'Demo',
                'email': 'demo@tejosolimpica.com',
                'tipo_usuario': 'admin'
            }
        )
        if created:
            user.set_password('demo123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Usuario demo creado: demo_user/demo123'))
        
        # Simular el middleware
        thread = current_thread()
        thread.user = user

        # Crear algunas categorías
        self.stdout.write('\n1. Creando categorías...')
        categorias = []
        for nombre in ['Tejos Profesionales', 'Tejos Recreativos', 'Accesorios', 'Equipamiento']:
            cat, created = Categoria.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': f'Categoría de {nombre}'}
            )
            categorias.append(cat)
            if created:
                self.stdout.write(f'   ✓ {nombre}')

        # Crear productos y modificarlos
        self.stdout.write('\n2. Creando y modificando productos...')
        productos_nombres = [
            'Tejo Profesional Premium',
            'Tejo Recreativo Estándar',
            'Mecha para Tejo',
            'Cancha Portátil',
            'Tablero de Puntuación'
        ]
        
        for i, nombre in enumerate(productos_nombres):
            precio_inicial = random.randint(50, 500) * 1000
            stock_inicial = random.randint(5, 50)
            
            producto, created = Producto.objects.get_or_create(
                codigo=f'DEMO-{i+1:03d}',
                defaults={
                    'nombre': nombre,
                    'descripcion': f'Producto de demostración: {nombre}',
                    'precio': precio_inicial,
                    'stock': stock_inicial,
                    'categoria': random.choice(categorias)
                }
            )
            
            if created:
                self.stdout.write(f'   ✓ {nombre} (${precio_inicial}, Stock: {stock_inicial})')
            
            # Hacer algunas modificaciones
            for _ in range(random.randint(1, 3)):
                producto.precio = random.randint(50, 500) * 1000
                producto.stock = random.randint(5, 100)
                producto.save()

        # Crear clientes
        self.stdout.write('\n3. Creando clientes...')
        clientes = []
        for i in range(5):
            cliente, created = Cliente.objects.get_or_create(
                email=f'cliente{i+1}@example.com',
                defaults={
                    'nombre': f'Cliente{i+1}',
                    'apellido': f'Apellido{i+1}',
                    'telefono': f'300{random.randint(1000000, 9999999)}',
                    'direccion': f'Calle {i+1} # {random.randint(10, 99)}-{random.randint(10, 99)}'
                }
            )
            clientes.append(cliente)
            if created:
                self.stdout.write(f'   ✓ {cliente}')

        # Crear pedidos
        self.stdout.write('\n4. Creando pedidos...')
        estados = ['pendiente', 'en_proceso', 'completado']
        for i in range(10):
            pedido = Pedido.objects.create(
                cliente=random.choice(clientes),
                estado=random.choice(estados)
            )
            
            # Cambiar estado algunas veces
            for estado in estados:
                if random.random() > 0.5:
                    pedido.estado = estado
                    pedido.save()
            
            self.stdout.write(f'   ✓ Pedido #{pedido.id}')

        # Limpiar thread
        if hasattr(thread, 'user'):
            delattr(thread, 'user')

        # Mostrar estadísticas
        self.stdout.write(self.style.SUCCESS('\n=== Generación Completada ==='))
        self.stdout.write(f'\nEstadísticas:')
        self.stdout.write(f'- Categorías: {Categoria.objects.count()}')
        self.stdout.write(f'- Productos: {Producto.objects.count()}')
        self.stdout.write(f'- Clientes: {Cliente.objects.count()}')
        self.stdout.write(f'- Pedidos: {Pedido.objects.count()}')
        self.stdout.write(f'- Auditorías registradas: {AuditLog.objects.count()}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Datos de demostración generados exitosamente!'))
        self.stdout.write('\nPuede acceder al admin en: http://localhost:8000/admin/')
        self.stdout.write('Usuario: demo_user / Contraseña: demo123')
