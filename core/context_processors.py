"""
Context Processors para pasar variables globales a todas las plantillas
"""

from core.utils import formato_pesos


def variables_globales(request):
    """
    Agrega variables globales disponibles en todas las plantillas
    """
    return {
        'formato_pesos': formato_pesos,
        'CURRENCY': 'COP',
        'CURRENCY_SYMBOL': '$',
    }