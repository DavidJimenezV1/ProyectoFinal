from rest_framework import serializers
from .models import Cliente, Pedido, DetallePedido

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class DetallePedidoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.ReadOnlyField(source='producto.nombre')
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = DetallePedido
        fields = ['id', 'producto', 'producto_nombre', 'cantidad', 
                  'precio_unitario', 'total']
    
    def get_total(self, obj):
        return obj.cantidad * obj.precio_unitario

class PedidoSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.ReadOnlyField(source='cliente.__str__')
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Pedido
        fields = ['id', 'cliente', 'cliente_nombre', 'fecha_pedido', 
                  'fecha_entrega', 'estado', 'observaciones', 'detalles']