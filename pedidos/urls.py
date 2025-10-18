from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet, PedidoViewSet, DetallePedidoViewSet

router = DefaultRouter()
router.register('clientes', ClienteViewSet)
router.register('pedidos', PedidoViewSet)
router.register('detalles', DetallePedidoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]