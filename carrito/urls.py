from django.urls import path
from . import views

app_name = 'carrito'

urlpatterns = [
    path('', views.ver_carrito, name='ver_carrito'),
    path('agregar/<int:producto_id>/', views.agregar_producto, name='agregar'),
    path('eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar'),
    path('actualizar/<int:producto_id>/', views.actualizar_cantidad, name='actualizar'),
    path('vaciar/', views.vaciar_carrito, name='vaciar'),
    path('convertir/', views.convertir_a_cotizacion, name='convertir'),
]