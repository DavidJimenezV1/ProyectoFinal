from django.urls import path
from . import views

app_name = 'cotizaciones'

urlpatterns = [
    path('', views.CotizacionListView.as_view(), name='lista_cotizaciones'),
    path('<int:pk>/', views.CotizacionDetailView.as_view(), name='detalle_cotizacion'),
    path('nueva/', views.nueva_cotizacion, name='nueva_cotizacion'),
    path('<int:pk>/responder/', views.responder_cotizacion, name='responder_cotizacion'),
    path('desde-carrito/', views.nueva_cotizacion_desde_carrito, name='nueva_cotizacion_desde_carrito'),
    path('<int:pk>/descargar-pdf/', views.descargar_cotizacion_pdf, name='descargar_pdf'),
]
