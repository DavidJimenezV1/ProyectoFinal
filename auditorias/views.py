from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Auditoria


@staff_member_required
def dashboard_auditorias(request):
    """
    Vista del dashboard de auditorías con estadísticas y registros recientes.
    """
    # Obtener parámetros de filtrado
    dias = int(request.GET.get('dias', 7))
    fecha_desde = timezone.now() - timedelta(days=dias)
    
    # Estadísticas generales
    total_auditorias = Auditoria.objects.filter(fecha_hora__gte=fecha_desde).count()
    
    # Contar por tipo de acción
    stats_acciones = Auditoria.objects.filter(
        fecha_hora__gte=fecha_desde
    ).values('accion').annotate(
        total=Count('id')
    )
    
    # Contar por tipo de modelo
    stats_modelos = Auditoria.objects.filter(
        fecha_hora__gte=fecha_desde
    ).values(
        'content_type__app_label',
        'content_type__model'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:10]
    
    # Usuarios más activos
    usuarios_activos = Auditoria.objects.filter(
        fecha_hora__gte=fecha_desde,
        usuario__isnull=False
    ).values(
        'usuario__username',
        'usuario__email'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:10]
    
    # Registros recientes
    registros_recientes = Auditoria.objects.select_related(
        'usuario', 'content_type'
    ).filter(
        fecha_hora__gte=fecha_desde
    ).order_by('-fecha_hora')[:50]
    
    context = {
        'total_auditorias': total_auditorias,
        'stats_acciones': stats_acciones,
        'stats_modelos': stats_modelos,
        'usuarios_activos': usuarios_activos,
        'registros_recientes': registros_recientes,
        'dias': dias,
        'fecha_desde': fecha_desde,
    }
    
    return render(request, 'auditorias/dashboard.html', context)


@staff_member_required
def detalle_auditoria(request, auditoria_id):
    """
    Vista de detalle de una auditoría específica.
    """
    from django.shortcuts import get_object_or_404
    
    auditoria = get_object_or_404(Auditoria, id=auditoria_id)
    
    # Obtener auditorías relacionadas con el mismo objeto
    auditorias_relacionadas = Auditoria.objects.filter(
        content_type=auditoria.content_type,
        object_id=auditoria.object_id
    ).exclude(id=auditoria.id).order_by('-fecha_hora')[:10]
    
    context = {
        'auditoria': auditoria,
        'auditorias_relacionadas': auditorias_relacionadas,
    }
    
    return render(request, 'auditorias/detalle.html', context)


@staff_member_required
def historial_objeto(request, content_type_id, object_id):
    """
    Vista del historial completo de un objeto específico.
    """
    from django.contrib.contenttypes.models import ContentType
    from django.shortcuts import get_object_or_404
    
    content_type = get_object_or_404(ContentType, id=content_type_id)
    
    auditorias = Auditoria.objects.filter(
        content_type=content_type,
        object_id=object_id
    ).select_related('usuario').order_by('-fecha_hora')
    
    context = {
        'content_type': content_type,
        'object_id': object_id,
        'auditorias': auditorias,
    }
    
    return render(request, 'auditorias/historial.html', context)
