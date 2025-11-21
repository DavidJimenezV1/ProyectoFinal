import django_filters
from django.utils import timezone
from datetime import timedelta
from auditorias.models import AuditLog

class DateRangeFilter(django_filters.FilterSet):
    """Filtro por rangos de fecha"""
    
    RANGE_CHOICES = [
        ('today', 'Hoy'),
        ('week', 'Esta semana'),
        ('month', 'Este mes'),
        ('year', 'Este año'),
        ('all', 'Todo el tiempo'),
    ]
    
    fecha_rango = django_filters.ChoiceFilter(
        choices=RANGE_CHOICES,
        method='filter_by_date_range',
        label='Rango de fecha'
    )
    
    class Meta:
        model = AuditLog
        fields = ['usuario', 'accion', 'modelo']
    
    def filter_by_date_range(self, queryset, name, value):
        now = timezone.now()
        
        if value == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return queryset.filter(timestamp__gte=start_date)
        elif value == 'week':
            start_date = now - timedelta(days=7)
            return queryset.filter(timestamp__gte=start_date)
        elif value == 'month':
            start_date = now - timedelta(days=30)
            return queryset.filter(timestamp__gte=start_date)
        elif value == 'year':
            start_date = now - timedelta(days=365)
            return queryset.filter(timestamp__gte=start_date)
        else:
            return queryset