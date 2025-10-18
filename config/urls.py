from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import HomePage, AdminDashboard, dashboard_stats, error_404, error_500
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Configuración del schema para documentación API
schema_view = get_schema_view(
   openapi.Info(
      title="API Tejos Olímpica",
      default_version='v1',
      description="API para gestión de inventario y pedidos",
      contact=openapi.Contact(email="contacto@tejosolimpica.com"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('', HomePage.as_view(), name='home'),  # Página principal pública
    path('dashboard/', AdminDashboard.as_view(), name='dashboard'),  # Dashboard administrativo
    path('admin/', admin.site.urls),  # Panel de administración de Django
    path('usuarios/', include('usuarios.urls')),
    path('catalogo/', include('catalogo.urls', namespace='catalogo')),
    path('carrito/', include('carrito.urls', namespace='carrito')),
    path('cotizaciones/', include('cotizaciones.urls', namespace='cotizaciones')),
    
    # Incluir las URLs de inventario (incluye la nueva API de precios)
    path('', include('inventario.urls')),
    
    path('api/pedidos/', include('pedidos.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/dashboard-stats/', dashboard_stats, name='dashboard-stats'),
    
    # Documentación API
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Configurar los archivos estáticos y media en modo desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Configurar páginas de error personalizadas
handler404 = error_404
handler500 = error_500