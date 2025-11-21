from django.urls import path
from . import views

app_name = 'auditorias'

urlpatterns = [
    path('', views.dashboard_auditorias, name='dashboard'),
    path('detalle/<int:auditoria_id>/', views.detalle_auditoria, name='detalle'),
    path('historial/<int:content_type_id>/<int:object_id>/', views.historial_objeto, name='historial'),
]
