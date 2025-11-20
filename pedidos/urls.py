from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet, PedidoViewSet, DetallePedidoViewSet
from .views import descargar_pedido_pdf

router = DefaultRouter()
router.register('clientes', ClienteViewSet)
router.register('pedidos', PedidoViewSet)
router.register('detalles', DetallePedidoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('pedidos/<int:pk>/descargar-pdf/', descargar_pedido_pdf, name='descargar_pedido_pdf'),
]
