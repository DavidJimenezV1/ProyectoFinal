from rest_framework import serializers
from .models import Categoria, Producto

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.ReadOnlyField(source='categoria.nombre')
    
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'codigo', 'descripcion', 'categoria', 
                  'categoria_nombre', 'precio', 'stock', 'stock_minimo', 
                  'fecha_creacion', 'fecha_actualizacion']