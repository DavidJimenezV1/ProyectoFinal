from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=5)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
    
    def imagen_principal(self):
        """Retorna la imagen principal del producto o None si no existe"""
        img = self.imagenes.filter(es_principal=True).first()
        if img:
            return img
        # Si no hay imagen principal, devolver la primera imagen
        return self.imagenes.first()

class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='productos/')
    es_principal = models.BooleanField(default=False, verbose_name="Imagen principal")
    orden = models.IntegerField(default=0, verbose_name="Orden de visualización")
    titulo = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        ordering = ['orden']
        verbose_name = "Imagen de producto"
        verbose_name_plural = "Imágenes de productos"
    
    def __str__(self):
        return f"Imagen de {self.producto.nombre} ({'Principal' if self.es_principal else 'Secundaria'})"
    
    def save(self, *args, **kwargs):
        # Si esta imagen se marca como principal, desmarcar las demás
        if self.es_principal:
            ImagenProducto.objects.filter(
                producto=self.producto, 
                es_principal=True
            ).exclude(id=self.id).update(es_principal=False)
        
        super().save(*args, **kwargs)