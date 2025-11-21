"""
Utilidades globales de la aplicación
Formatos de moneda, conversiones, etc.
"""

from django.conf import settings


def formato_pesos(valor, incluir_decimales=False):
    """
    Convierte un valor a pesos colombianos formateado
    
    Args:
        valor: Número a convertir
        incluir_decimales: Si True, incluye 2 decimales
    
    Returns:
        String con formato: $1.234.567 o $1.234.567,89
    """
    try:
        if valor is None:
            return "$0" if not incluir_decimales else "$0,00"
        
        valor_float = float(valor)
        
        if incluir_decimales:
            # Formato: $1.234.567,89
            formateado = f"${valor_float:,.2f}"
            # Intercambiar separadores
            return formateado.replace(",", "@").replace(".", ",").replace("@", ".")
        else:
            # Formato: $1.234.567
            return f"${valor_float:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return "N/A"


def convertir_pesos_a_numero(valor_string):
    """
    Convierte un string con formato de pesos a número
    
    Args:
        valor_string: String como "$1.234.567" o "$1.234.567,89"
    
    Returns:
        Float con el valor numérico
    """
    try:
        # Remover símbolo de pesos
        sin_simbolo = valor_string.replace("$", "").strip()
        # Remover puntos (separadores de miles)
        sin_puntos = sin_simbolo.replace(".", "")
        # Reemplazar coma por punto (decimal)
        numero = sin_puntos.replace(",", ".")
        return float(numero)
    except (ValueError, TypeError, AttributeError):
        return 0.0


def es_numero_valido(valor):
    """Verifica si un valor es un número válido"""
    try:
        float(valor)
        return True
    except (ValueError, TypeError):
        return False