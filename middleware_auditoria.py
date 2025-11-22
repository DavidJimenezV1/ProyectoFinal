"""
Middleware para capturar el usuario actual en cada request.
Esto permite que los signals puedan acceder al usuario.
"""

from auditorias.apps_signals import establecer_usuario_actual

class AuditoriaMiddleware:
    """Middleware que captura el usuario actual"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Capturar el usuario antes de procesar la request
        if request.user.is_authenticated:
            establecer_usuario_actual(request.user)
        else:
            establecer_usuario_actual(None)
        
        response = self.get_response(request)
        return response