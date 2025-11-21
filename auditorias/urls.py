from django.urls import path
from auditorias import views

app_name = 'auditorias'

urlpatterns = [
    path('dashboard/', views.dashboard_auditoria, name='dashboard'),
]