from django.urls import path
from .views import PedidoDetailView, descargar_pedido_pdf

# Este app_name es crucial para que el botón funcione
app_name = 'pedidos'

urlpatterns = [
    path('<int:pk>/', PedidoDetailView.as_view(), name='detalle_pedido'),
    path('<int:pk>/descargar-pdf/', descargar_pedido_pdf, name='descargar_pedido_pdf'),
]
