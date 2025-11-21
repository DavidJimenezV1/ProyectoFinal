"""
Middleware para capturar el usuario actual en cada solicitud
y hacer que esté disponible para los signals de auditoría.
"""
from threading import current_thread


class CurrentUserMiddleware:
    """
    Middleware que almacena el usuario actual en el thread local
    para que esté disponible en los signals.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Almacenar el usuario en el thread local
        thread = current_thread()
        thread.user = getattr(request, 'user', None)
        
        response = self.get_response(request)
        
        # Limpiar el thread local
        if hasattr(thread, 'user'):
            delattr(thread, 'user')
        
        return response
