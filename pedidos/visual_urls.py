from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    # Lista pública de pedidos: /pedidos/
    path('', views.lista_pedidos, name='lista_pedidos'),

    # RUTA LEGACY: /pedidos/1/  <-- restaurada para compatibilidad
    path('<int:pk>/', views.PedidoDetailView.as_view(), name='detalle_pedido'),

    # Alias explícito (nueva ruta que añadimos): /pedidos/pedido/1/
    # No usamos el mismo 'name' aquí para evitar confusión en reverses.
    path('pedido/<int:pk>/', views.PedidoDetailView.as_view(), name='detalle_pedido_alt'),

    # Editar y descargar PDF
    path('pedido/<int:pk>/editar/', views.editar_pedido, name='editar_pedido'),
    path('pedido/<int:pk>/descargar-pdf/', views.descargar_pedido_pdf, name='descargar_pedido_pdf'),
]
