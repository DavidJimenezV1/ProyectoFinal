from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import HomePage
from inventario.views import obtener_precio_producto, get_producto_precio

urlpatterns = [
    # ==================== HOME ====================
    path('', HomePage.as_view(), name='home'),
    
    # ==================== ADMIN ====================
    path('admin/', admin.site.urls),
    
    # ==================== API - PRODUCTOS ====================
    path('api/productos/<int:producto_id>/precio/', get_producto_precio, name='api_producto_precio'),
    path('api/productos/<int:producto_id>/obtener-precio/', obtener_precio_producto, name='obtener_precio_producto'),
    
    # ==================== APPS ====================
    path('', include('core.urls')),
    path('auth/', include('usuarios.urls')),
    path('inventario/', include('inventario.urls')),
    path('pedidos/', include('pedidos.urls')),
    path('catalogo/', include('catalogo.urls')),
    path('cotizaciones/', include('cotizaciones.urls')),
    path('carrito/', include('carrito.urls')),
    path('ventas/', include('ventas.urls')),
]

# ==================== ARCHIVOS ESTÁTICOS Y MEDIA ====================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)