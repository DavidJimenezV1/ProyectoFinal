from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('', views.lista_pedidos, name='lista_pedidos'),
    path('pedido/<int:pk>/', views.PedidoDetailView.as_view(), name='detalle_pedido'),
    path('pedido/<int:pk>/editar/', views.editar_pedido, name='editar_pedido'),
    path('pedido/<int:pk>/descargar-pdf/', views.descargar_pedido_pdf, name='descargar_pedido_pdf'),
]
