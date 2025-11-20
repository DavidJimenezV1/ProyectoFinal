from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    path('', views.ProductoListView.as_view(), name='lista_productos'),
    path('<int:pk>/', views.ProductoDetailView.as_view(), name='detalle_producto'),
]