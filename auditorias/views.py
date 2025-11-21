from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from auditorias.models import AuditLog

@staff_required
def dashboard_auditoria(request):
    """Dashboard de auditoría con estadísticas"""
    
    # Obtener rango de fechas
    rango_dias = int(request.GET.get('rango', 30))
    fecha_inicio = timezone.now() - timedelta(days=rango_dias)
    
    # Logs del período
    logs = AuditLog.objects.filter(timestamp__gte=fecha_inicio)
    
    # Estadísticas
    total_acciones = logs.count()
    acciones_por_tipo = logs.values('accion').annotate(count=Count('accion')).order_by('-count')
    acciones_por_usuario = logs.values('usuario__username').annotate(count=Count('usuario')).order_by('-count')[:10]
    modelos_mas_modificados = logs.values('modelo').annotate(count=Count('modelo')).order_by('-count')
    
    contexto = {
        'total_acciones': total_acciones,
        'acciones_por_tipo': acciones_por_tipo,
        'acciones_por_usuario': acciones_por_usuario,
        'modelos_mas_modificados': modelos_mas_modificados,
        'rango_dias': rango_dias,
        'fecha_inicio': fecha_inicio,
    }
    
    return render(request, 'auditorias/dashboard.html', contexto)