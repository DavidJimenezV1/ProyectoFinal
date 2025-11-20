from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    # Vistas existentes (si las tienes)
    path('productos/', views.ProductoListView.as_view(), name='producto_list'),
    path('productos/<int:pk>/', views.ProductoDetailView.as_view(), name='producto_detail'),
    
    # Nueva API de precios
    path('api/productos/<int:producto_id>/precio/', views.obtener_precio_producto, name='producto_precio'),
]