"""
Archivo de debug para verificar que los signals se están ejecutando
"""

def test_signals():
    """Función para testear si los signals funcionan"""
    from auditorias.models import AuditLog
    from django.contrib.auth.models import User
    from cotizaciones.models import DetalleCotizacion, Cotizacion
    
    # Obtener un usuario
    usuario = User.objects.first()
    if not usuario:
        print("❌ No hay usuarios en el sistema")
        return
    
    print(f"✅ Usuario encontrado: {usuario.username}")
    
    # Obtener una cotización
    cotizacion = Cotizacion.objects.first()
    if not cotizacion:
        print("❌ No hay cotizaciones")
        return
    
    print(f"✅ Cotización encontrada: #{cotizacion.id}")
    
    # Ver logs de auditoría
    logs = AuditLog.objects.filter(modelo='Cotizacion').order_by('-timestamp')[:10]
    print(f"\n📊 Últimos 10 registros de auditoría de Cotizaciones:")
    for log in logs:
        print(f"  - {log.timestamp}: {log.accion} - {log.objeto_nombre} por {log.usuario}")
    
    if not logs:
        print("  ❌ No hay registros de auditoría para cotizaciones")